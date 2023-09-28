from django.contrib import admin
from .models import CustomUser, Advisor

admin.site.register(CustomUser)
admin.site.register(Advisor)
