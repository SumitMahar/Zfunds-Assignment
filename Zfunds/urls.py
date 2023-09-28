from django.contrib import admin
from django.urls import path, include
from Zfunds.Product import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("Zfunds.Product.urls")),
    path("api/users/", include("Zfunds.Accounts.urls")),

]
