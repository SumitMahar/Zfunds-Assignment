from django.db import models

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
    


