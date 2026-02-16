import django_filters
from .models import Expense, Income, Shop, Cloth,Category,Subcategory

class ExpenseFilter(django_filters.FilterSet):
    shop = django_filters.ModelChoiceFilter(queryset=Shop.objects.all())
    cloth__subcategory__category = django_filters.ModelChoiceFilter(queryset=Category.objects.all(), label='Category')
    cloth__subcategory = django_filters.ModelChoiceFilter(queryset=Subcategory.objects.all(), label='Subcategory')
    date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Expense
        fields = ['shop', 'cloth__subcategory__category', 'cloth__subcategory', 'date']

class IncomeFilter(django_filters.FilterSet):
    shop = django_filters.ModelChoiceFilter(queryset=Shop.objects.all())
    cloth__subcategory__category = django_filters.ModelChoiceFilter(queryset=Category.objects.all(), label='Category')
    cloth__subcategory = django_filters.ModelChoiceFilter(queryset=Subcategory.objects.all(), label='Subcategory')
    date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Income
        fields = ['shop', 'cloth__subcategory__category', 'cloth__subcategory', 'date']