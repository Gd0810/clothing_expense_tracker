from django.db import models
from django.contrib.auth.models import User
from shops.models import Shop  # Import Shop from shops app

# Category Model (Men, Women)
class Category(models.Model):
    name = models.CharField(max_length=50)  # Men or Women

    def __str__(self):
        return self.name

# Subcategory Model (Adult, Child)
class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)  # Adult or Child

    def __str__(self):
        return f"{self.category.name} - {self.name}"

# Cloth Model
class Cloth(models.Model):
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.subcategory} - {self.name}"

# Expense Model
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='expenses')
    cloth = models.ForeignKey(Cloth, on_delete=models.CASCADE, related_name='expenses')
    quantity = models.PositiveIntegerField(default=1)  # Added quantity field
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shop.name} - {self.cloth.name} - {self.quantity} - {self.amount}"

# Income Model
class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='incomes')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='incomes')
    cloth = models.ForeignKey(Cloth, on_delete=models.CASCADE, related_name='incomes')
    quantity = models.PositiveIntegerField(default=1)  # Added quantity field
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.shop.name} - {self.cloth.name} - {self.quantity} - {self.amount}"