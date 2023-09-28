from django.db import models
from Zfunds.Accounts.models import CustomUser, Advisor

class Category(models.Model):
    name = models.CharField(max_length=150, blank=False, null=False)

    class Meta:
        db_table = "category" # Table name in database
        verbose_name_plural = "Categories" # Plural name for the model

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=False)

    class Meta:
        db_table = "product"
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} | {self.category}"
    

class Order(models.Model):
    advisor = models.ForeignKey(Advisor, on_delete=models.CASCADE)
    client = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    unique_link = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"Order for: {self.product} | Client: {self.client} | Advisor: {self.advisor}"
