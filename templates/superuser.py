python manage.py shell -c
from django.contrib.auth import get_user_model;
User=get_user_model();
u=User.objects.get(email='delinoiskadhaffimacarthur@outlook.com ');
u.is_staff=True;
u.is_superuser=True;
u.save()
