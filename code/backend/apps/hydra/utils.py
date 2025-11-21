from django.http import JsonResponse

def health_check(request):
    """Simple health check for hydra integration app"""
    return JsonResponse({"status": "healthy", "service": "hydra-integration"}, status=200)