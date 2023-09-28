from django.contrib import admin
from django.urls import path
from Zfunds.Product import views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path(r"product/", views.ProductView.as_view(), name="products"),
    path("", SpectacularAPIView.as_view(), name="schema"),
    path("product/purchase", views.PurchaseProductView.as_view(), name="product-purchase"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),

]
