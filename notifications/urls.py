from django.urls import path
from .views import notification_list, mark_notification_as_read, delete_notification

app_name = "notifications"

urlpatterns = [
    path("", notification_list, name="notification_list"),
    path("<int:notification_id>/read/", mark_notification_as_read, name="mark_as_read"),
    path("<int:notification_id>/delete/", delete_notification, name="delete_notification"),
]