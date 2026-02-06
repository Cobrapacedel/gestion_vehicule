from django.urls import path
from .views import notification_list, notification_mark_as_read, notification_delete, notification_detail

app_name = "notifications"

urlpatterns = [
    path("", notification_list, name="notification_list"),
    path("<int:notification_id>/read/", notification_mark_as_read, name="mark_as_read"),
    path("detail/<int:notification_id>/", notification_detail, name="notification_detail"),
    path("<int:notification_id>/delete/", notification_delete, name="notification_delete"),
]
