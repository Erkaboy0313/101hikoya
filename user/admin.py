from django.contrib import admin
from .models import Role,Writer,Reader,CustomUser,Admin

@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username','role']
    search_fields = ['username']

admin.site.register(Reader)
admin.site.register(Admin)
admin.site.register(Role)
admin.site.register(Writer)
# Register your models here.
