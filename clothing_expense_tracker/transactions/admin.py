from django.contrib import admin
from .models import Category, Subcategory, Cloth, Expense, Income

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')
    ordering = ('category__name', 'name')

@admin.register(Cloth)
class ClothAdmin(admin.ModelAdmin):
    list_display = ('name', 'subcategory', 'category_name')
    list_filter = ('subcategory', 'subcategory__category')
    search_fields = ('name', 'subcategory__name', 'subcategory__category__name')
    ordering = ('subcategory__category__name', 'subcategory__name', 'name')

    def category_name(self, obj):
        return obj.subcategory.category.name
    category_name.short_description = 'Category'

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('shop', 'cloth', 'cloth_category', 'cloth_subcategory', 'amount', 'date')
    list_filter = ('shop', 'user', 'cloth__subcategory__category', 'cloth__subcategory', 'date')
    search_fields = ('shop__name', 'cloth__name', 'cloth__subcategory__category__name', 'cloth__subcategory__name', 'description')
    ordering = ('-date', 'shop__name')
    date_hierarchy = 'date'

    def cloth_category(self, obj):
        return obj.cloth.subcategory.category.name
    cloth_category.short_description = 'Category'

    def cloth_subcategory(self, obj):
        return obj.cloth.subcategory.name
    cloth_subcategory.short_description = 'Subcategory'

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('shop', 'cloth', 'cloth_category', 'cloth_subcategory', 'amount', 'date')
    list_filter = ('shop', 'user', 'cloth__subcategory__category', 'cloth__subcategory', 'date')
    search_fields = ('shop__name', 'cloth__name', 'cloth__subcategory__category__name', 'cloth__subcategory__name', 'description')
    ordering = ('-date', 'shop__name')
    date_hierarchy = 'date'

    def cloth_category(self, obj):
        return obj.cloth.subcategory.category.name
    cloth_category.short_description = 'Category'

    def cloth_subcategory(self, obj):
        return obj.cloth.subcategory.name
    cloth_subcategory.short_description = 'Subcategory'