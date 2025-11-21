```bash
# makemigrations
docker exec -it initial_django_vue_backend bash -c 'cd /app && python manage.py makemigrations'

# Create a new app
docker exec -it initial_django_vue_backend bash -c 'cd /app && python manage.py startapp hydra apps/hydra'
```