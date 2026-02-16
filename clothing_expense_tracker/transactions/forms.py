from django import forms
from django.db.models import Sum
from .models import Expense, Income, Cloth, Shop

class ExpenseForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}))

    class Meta:
        model = Expense
        fields = ['shop', 'cloth', 'quantity', 'amount', 'date', 'description']
        widgets = {
            'shop': forms.Select(attrs={'class': 'form-control'}),
            'cloth': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['shop'].queryset = Shop.objects.filter(user=user)
            self.fields['cloth'].queryset = Cloth.objects.all()

class IncomeForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=0, widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}))

    class Meta:
        model = Income
        fields = ['shop', 'cloth', 'quantity', 'amount', 'date', 'description']
        widgets = {
            'shop': forms.Select(attrs={'class': 'form-control'}),
            'cloth': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['shop'].queryset = Shop.objects.filter(user=user)
            cloth_data = Expense.objects.filter(user=user).values('cloth').annotate(total_purchased=Sum('quantity'))
            cloth_sold = Income.objects.filter(user=user).values('cloth').annotate(total_sold=Sum('quantity'))
            cloth_stock = {}
            for cd in cloth_data:
                cloth_id = cd['cloth']
                purchased = cd['total_purchased'] or 0
                sold = next((cs['total_sold'] or 0 for cs in cloth_sold if cs['cloth'] == cloth_id), 0)
                remaining = purchased - sold
                if remaining > 0:
                    cloth_stock[cloth_id] = remaining
            self.fields['cloth'].queryset = Cloth.objects.filter(id__in=cloth_stock.keys())
            for field in self.fields['cloth'].queryset:
                field.remaining_stock = cloth_stock.get(field.id, 0)