from django.contrib import admin
from .models import ProjectInfo

@admin.register(ProjectInfo)
class ProjectInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'developer', 'last_update')
    readonly_fields = ('creation_date', 'last_update')