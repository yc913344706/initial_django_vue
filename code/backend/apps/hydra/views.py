from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from lib.request_tool import pub_get_request_body, pub_success_response, pub_error_response
from apps.user.models import User
from apps.myAuth.token_utils import TokenManager
from apps.perm.utils import get_user_perm_json_all
from apps.ldapauth.ldap_utils import LdapAuthBackend
from apps.ldapauth.models import LdapConfig
from apps.audit.utils import add_audit_log
from lib.log import color_logger
from backend.settings import config_data
import json
import requests


@csrf_exempt
@require_http_methods(["GET", "POST"])
def hydra_login(request):
    """
    Hydra login endpoint
    When Hydra needs to authenticate a user, it will redirect to this endpoint
    """
    try:
        body = pub_get_request_body(request)

        if request.method == 'GET':
            # GET request from Hydra - display login form or return login URL
            login_challenge = request.GET.get('login_challenge')
            if not login_challenge:
                return pub_error_response(15001, msg='Missing login challenge')

            # Get login request from Hydra to check if user is already authenticated
            hydra_admin_url = "http://hydra:4445"
            hydra_login_request_url = f"{hydra_admin_url}/oauth2/auth/requests/login"

            try:
                response = requests.get(f"{hydra_login_request_url}/{login_challenge}", allow_redirects=True)
                if response.status_code == 200:
                    login_request = response.json()
                    # Check if user is already authenticated in our app
                    # For now, we'll always redirect to login form
                    return pub_success_response({
                        'login_challenge': login_challenge,
                        'need_login': True,
                        'message': 'User needs to authenticate'
                    })
                else:
                    return pub_error_response(15002, msg=f'Invalid login challenge: Status {response.status_code}')
            except Exception as e:
                color_logger.error(f"Failed to fetch login request from Hydra: {e}")
                return pub_error_response(15003, msg='Failed to communicate with Hydra')

        elif request.method == 'POST':
            # POST request with username/password from login form
            username = body.get('username')
            password = body.get('password')
            login_challenge = body.get('login_challenge')

            if not all([username, password, login_challenge]):
                return pub_error_response(15004, msg='Missing required parameters: username, password, login_challenge')

            # Authenticate user using existing logic from myAuth app
            user_obj = None

            # Check LDAP configuration
            ldap_config = LdapConfig.objects.filter(enabled=True).first()

            if ldap_config:
                # First check if user exists locally
                local_user = User.objects.filter(username=username).first()

                if local_user and local_user.is_ldap:
                    # LDAP user
                    ldap_backend = LdapAuthBackend()
                    user_obj = ldap_backend.authenticate(username=username, password=password)
                elif local_user and not local_user.is_ldap:
                    # Local user
                    if local_user.check_password(password):
                        user_obj = local_user
                else:
                    # User not in local DB, try LDAP
                    ldap_backend = LdapAuthBackend()
                    user_obj = ldap_backend.authenticate(username=username, password=password)
            else:
                # No LDAP, only local auth
                local_user = User.objects.filter(username=username).first()
                if local_user and not local_user.is_ldap and local_user.check_password(password):
                    user_obj = local_user

            if not user_obj:
                # Log failed login attempt
                add_audit_log(
                    action='LOGIN_FAILED',
                    operator_username=username,
                    detail={'message': 'OAuth2 login attempt failed', 'source': 'hydra'},
                    request=request
                )
                return pub_error_response(15005, msg='Invalid username or password')

            # Authentication successful
            # Accept the login request with Hydra
            hydra_admin_url = "http://hydra:4445"
            hydra_login_accept_url = f"{hydra_admin_url}/oauth2/auth/requests/login/accept"

            try:
                accept_request_data = {
                    'subject': user_obj.username,
                    'remember': True,
                    'remember_for': 3600,  # Remember for 1 hour
                    'session': {
                        'username': user_obj.username,
                        'user_uuid': str(user_obj.uuid),
                    }
                }

                response = requests.put(f"{hydra_login_accept_url}?login_challenge={login_challenge}",
                                       json=accept_request_data)

                if response.status_code == 200:
                    accept_response = response.json()

                    # Log successful OAuth2 login
                    add_audit_log(
                        action='LOGIN',
                        operator_username=user_obj.username,
                        detail={'message': 'OAuth2 login successful', 'source': 'hydra'},
                        request=request
                    )

                    return pub_success_response({
                        'redirect_to': accept_response.get('redirect_to')
                    })
                else:
                    color_logger.error(f"Failed to accept login request: {response.text}")
                    return pub_error_response(15006, msg='Failed to accept login request')
            except Exception as e:
                color_logger.error(f"Failed to communicate with Hydra: {e}")
                return pub_error_response(15007, msg='Failed to communicate with Hydra')

    except Exception as e:
        color_logger.error(f"Hydra login endpoint error: {e}", exc_info=True)
        return pub_error_response(15008, msg=f'Login endpoint error: {str(e)}')


@csrf_exempt
@require_http_methods(["GET", "POST"])
def hydra_consent(request):
    """
    Hydra consent endpoint
    When Hydra needs user consent for scopes, it will redirect to this endpoint
    """
    try:
        body = pub_get_request_body(request)

        if request.method == 'GET':
            # GET request from Hydra - get consent request
            consent_challenge = request.GET.get('consent_challenge')
            if not consent_challenge:
                return pub_error_response(15009, msg='Missing consent challenge')

            # Get consent request from Hydra
            hydra_admin_url = "http://hydra:4445"
            hydra_consent_request_url = f"{hydra_admin_url}/oauth2/auth/requests/consent"

            try:
                response = requests.get(f"{hydra_consent_request_url}/{consent_challenge}", allow_redirects=True)
                if response.status_code == 200:
                    consent_request = response.json()

                    # Get user permissions to determine what to consent to
                    user_identifier = consent_request.get('subject')
                    user = User.objects.filter(username=user_identifier).first()

                    if not user:
                        return pub_error_response(15010, msg='User not found')

                    user_permission_json = get_user_perm_json_all(user.uuid)

                    return pub_success_response({
                        'consent_challenge': consent_challenge,
                        'requested_scope': consent_request.get('requested_scope', []),
                        'user_permissions': user_permission_json.get('frontend', {}).get('resources', []),
                        'message': 'User needs to grant consent'
                    })
                else:
                    return pub_error_response(15011, msg=f'Invalid consent challenge: Status {response.status_code}')
            except Exception as e:
                color_logger.error(f"Failed to fetch consent request from Hydra: {e}")
                return pub_error_response(15012, msg='Failed to communicate with Hydra')

        elif request.method == 'POST':
            # POST request to grant consent
            consent_challenge = body.get('consent_challenge')
            grant_scope = body.get('grant_scope', [])
            remember = body.get('remember', False)
            remember_for = body.get('remember_for', 3600)

            if not consent_challenge:
                return pub_error_response(15013, msg='Missing consent challenge')

            # Accept the consent request with Hydra
            hydra_admin_url = "http://hydra:4445"
            hydra_consent_accept_url = f"{hydra_admin_url}/oauth2/auth/requests/consent/accept"

            try:
                accept_request_data = {
                    'grant_scope': grant_scope,
                    'remember': remember,
                    'remember_for': remember_for
                }

                response = requests.put(f"{hydra_consent_accept_url}?consent_challenge={consent_challenge}",
                                       json=accept_request_data)

                if response.status_code == 200:
                    accept_response = response.json()
                    return pub_success_response({
                        'redirect_to': accept_response.get('redirect_to')
                    })
                else:
                    color_logger.error(f"Failed to accept consent request: {response.text}")
                    return pub_error_response(15014, msg='Failed to accept consent request')
            except Exception as e:
                color_logger.error(f"Failed to communicate with Hydra: {e}")
                return pub_error_response(15015, msg='Failed to communicate with Hydra')

    except Exception as e:
        color_logger.error(f"Hydra consent endpoint error: {e}", exc_info=True)
        return pub_error_response(15016, msg=f'Consent endpoint error: {str(e)}')


@require_http_methods(["GET"])
def hydra_userinfo(request):
    """
    Hydra userinfo endpoint
    Provides user information for OIDC requests
    """
    try:
        # Get access token from the Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return pub_error_response(15017, msg='Invalid Authorization header')

        access_token = auth_header[7:]  # Remove 'Bearer ' prefix

        # Verify the access token using our existing token manager
        token_manager = TokenManager()
        payload = token_manager.verify_token(access_token)

        if not payload:
            return pub_error_response(15018, msg='Invalid or expired access token')

        username = payload.get('username')
        if not username:
            return pub_error_response(15019, msg='Token does not contain username')

        user = User.objects.filter(username=username).first()
        if not user:
            return pub_error_response(15020, msg='User not found')

        # Return user information according to OIDC standard
        user_info = {
            'sub': user.username,
            'username': user.username,
            'nickname': user.nickname,
            'email': user.email,
            'name': user.nickname or user.username,
            'preferred_username': user.username,
            'user_uuid': str(user.uuid),
            'open_id': str(user.uuid)
        }

        return JsonResponse(user_info)

    except Exception as e:
        color_logger.error(f"Hydra userinfo endpoint error: {e}", exc_info=True)
        return pub_error_response(15021, msg=f'Userinfo endpoint error: {str(e)}')


@require_http_methods(["GET"])
def hydra_logout(request):
    """
    Hydra logout endpoint
    Handles user logout
    """
    try:
        body = pub_get_request_body(request)
        logout_challenge = request.GET.get('logout_challenge')
        # For now, just acknowledge the logout
        if logout_challenge:
            hydra_admin_url = "http://hydra:4445"
            hydra_logout_accept_url = f"{hydra_admin_url}/oauth2/auth/requests/logout/accept"

            try:
                response = requests.put(f"{hydra_logout_accept_url}?logout_challenge={logout_challenge}", allow_redirects=True)
                if response.status_code == 200:
                    logout_response = response.json()
                    return pub_success_response({
                        'redirect_to': logout_response.get('redirect_to')
                    })
                else:
                    # If Hydra doesn't require accept, return success
                    color_logger.warning(f"Could not accept logout challenge: Status {response.status_code}")
                    pass
            except Exception as e:
                color_logger.warning(f"Could not accept logout challenge: {e}")

        return pub_success_response({
            'status': 'logged out',
            'message': 'User logged out from OAuth2 session'
        })

    except Exception as e:
        color_logger.error(f"Hydra logout endpoint error: {e}", exc_info=True)
        return pub_error_response(15022, msg=f'Logout endpoint error: {str(e)}')


@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
def manage_oauth2_client(request):
    """
    Manage OAuth2 clients
    This endpoint allows creating, reading, updating, and deleting OAuth2 clients in Hydra
    """
    try:
        body = pub_get_request_body(request)
        hydra_admin_url = "http://hydra:4445"

        if request.method == 'POST':
            # Create a new OAuth2 client
            client_data = {
                'client_id': body.get('client_id'),
                'client_name': body.get('client_name', ''),
                'client_secret': body.get('client_secret'),
                'grant_types': body.get('grant_types', ['authorization_code', 'refresh_token']),
                'response_types': body.get('response_types', ['code']),
                'redirect_uris': body.get('redirect_uris', []),
                'scope': body.get('scope', 'openid profile email'),
                'token_endpoint_auth_method': body.get('token_endpoint_auth_method', 'client_secret_post')
            }

            # Remove None values
            client_data = {k: v for k, v in client_data.items() if v is not None}

            response = requests.post(f"{hydra_admin_url}/admin/clients", json=client_data, allow_redirects=True)

            if response.status_code in [200, 201]:
                return pub_success_response(response.json(), msg='OAuth2 client created successfully')
            else:
                color_logger.error(f"Failed to create client: {response.text}")
                return pub_error_response(15023, msg=f'Failed to create client: Status {response.status_code}, {response.text}')

        elif request.method == 'GET':
            # Get a specific client or list all clients
            client_id = request.GET.get('client_id')
            color_logger.debug(f"Getting client. client_id: {client_id}")

            if client_id:
                response = requests.get(f"{hydra_admin_url}/admin/clients/{client_id}", allow_redirects=True)
                if response.status_code == 200:
                    return pub_success_response(response.json())
                else:
                    return pub_error_response(15024, msg=f'Failed to get client: Status {response.status_code}, {response.text}')
            else:
                color_logger.debug(f"No client_id provided")
                _url = f"{hydra_admin_url}/admin/clients"

                color_logger.debug(f"hydra url: {_url}")

                # List all clients
                response = requests.get(_url, allow_redirects=True)
                color_logger.debug(f"List all clients status: {response.status_code}, response: {response.text[:500] if response.text else 'No response body'}...")
                if response.status_code == 200:
                    return pub_success_response(response.json())
                else:
                    return pub_error_response(15025, msg=f'Failed to list clients: Status {response.status_code}, {response.text}')

        elif request.method == 'PUT':
            # Update an existing client
            client_id = body.get('client_id')
            if not client_id:
                return pub_error_response(15026, msg='client_id is required for update')

            # Check if this is a secret reset request
            if body.get('reset_secret'):
                # Generate a new secret and update only the secret
                import secrets
                import string

                # Generate a new secret
                new_secret = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

                secret_update_data = {
                    'client_secret': new_secret
                }

                response = requests.patch(f"{hydra_admin_url}/admin/clients/{client_id}", json=secret_update_data, allow_redirects=True)

                if response.status_code == 200:
                    result = response.json()
                    # Return the new secret separately for security notice
                    result['client_secret'] = new_secret
                    return pub_success_response(result, msg='OAuth2 client secret reset successfully')
                else:
                    color_logger.error(f"Failed to reset client secret: {response.text}")
                    return pub_error_response(15027, msg=f'Failed to reset client secret: Status {response.status_code}, {response.text}')
            else:
                # Regular update request
                update_data = {}
                if 'client_name' in body:
                    update_data['client_name'] = body['client_name']
                if 'client_secret' in body:
                    update_data['client_secret'] = body['client_secret']
                if 'grant_types' in body:
                    update_data['grant_types'] = body['grant_types']
                if 'response_types' in body:
                    update_data['response_types'] = body['response_types']
                if 'redirect_uris' in body:
                    update_data['redirect_uris'] = body['redirect_uris']
                if 'scope' in body:
                    update_data['scope'] = body['scope']

                response = requests.put(f"{hydra_admin_url}/admin/clients/{client_id}", json=update_data, allow_redirects=True)

                if response.status_code == 200:
                    return pub_success_response(response.json(), msg='OAuth2 client updated successfully')
                else:
                    color_logger.error(f"Failed to update client: {response.text}")
                    return pub_error_response(15027, msg=f'Failed to update client: Status {response.status_code}, {response.text}')

        elif request.method == 'DELETE':
            # Delete a client
            client_id = body.get('client_id')
            if not client_id:
                return pub_error_response(15028, msg='client_id is required for deletion')

            response = requests.delete(f"{hydra_admin_url}/admin/clients/{client_id}", allow_redirects=True)

            if response.status_code == 204:
                return pub_success_response(msg='OAuth2 client deleted successfully')
            else:
                return pub_error_response(15029, msg=f'Failed to delete client: Status {response.status_code}, {response.text}')

    except Exception as e:
        color_logger.error(f"Manage OAuth2 client endpoint error: {e}", exc_info=True)
        return pub_error_response(15030, msg=f'OAuth2 client management error: {str(e)}')
