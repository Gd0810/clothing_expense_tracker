from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense, Income, Cloth
from .forms import ExpenseForm, IncomeForm
from django_filters.views import FilterView
from .filters import ExpenseFilter, IncomeFilter
from django.db.models import Sum, Avg

@login_required
def expense_list(request):
    expenses = Expense.objects.filter(user=request.user)
    expense_filter = ExpenseFilter(request.GET, queryset=expenses)
    filtered_expenses = expense_filter.qs
    total_expense = filtered_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    average_expense = filtered_expenses.aggregate(Avg('amount'))['amount__avg'] or 0

    context = {
        'filter': expense_filter,
        'total_expense': total_expense,
        'average_expense': average_expense
    }
    return render(request, 'transactions/expense_list.html', context)

@login_required
def expense_create(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.quantity = form.cleaned_data['quantity']
            expense.save()
            return redirect('expense_list')
    else:
        form = ExpenseForm(user=request.user)
    return render(request, 'transactions/expense_form.html', {'form': form})

@login_required
def income_list(request):
    incomes = Income.objects.filter(user=request.user)
    income_filter = IncomeFilter(request.GET, queryset=incomes)
    filtered_incomes = income_filter.qs
    total_income = filtered_incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    average_income = filtered_incomes.aggregate(Avg('amount'))['amount__avg'] or 0

    context = {
        'filter': income_filter,
        'total_income': total_income,
        'average_income': average_income
    }
    return render(request, 'transactions/income_list.html', context)

from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from transactions.models import Income, Expense, Cloth
from django.db.models import Sum

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['shop', 'cloth', 'quantity', 'amount', 'date', 'description']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(IncomeForm, self).__init__(*args, **kwargs)

        if user:
            # ✅ Show only shops belonging to the logged-in user
            self.fields['shop'].queryset = self.fields['shop'].queryset.filter(user=user)

            # ✅ Calculate remaining stock for each cloth
            cloth_data = Expense.objects.filter(user=user).values('cloth').annotate(
                total_purchased=Sum('quantity')
            )
            cloth_sold = Income.objects.filter(user=user).values('cloth').annotate(
                total_sold=Sum('quantity')
            )

            cloth_stock = {}
            for cd in cloth_data:
                cloth_id = cd['cloth']
                purchased = cd['total_purchased'] or 0
                sold = next((cs['total_sold'] or 0 for cs in cloth_sold if cs['cloth'] == cloth_id), 0)
                remaining = purchased - sold
                if remaining > 0:  # Only include cloths with remaining stock
                    cloth_stock[cloth_id] = remaining

            # ✅ Filter cloths to only those with remaining stock
            self.fields['cloth'].queryset = Cloth.objects.filter(id__in=cloth_stock.keys())

            # Add custom attribute for stock display
            for field in self.fields['cloth'].queryset:
                field.remaining_stock = cloth_stock.get(field.id, 0)


@login_required
def income_create(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST, user=request.user)
        if form.is_valid():
            cloth_id = form.cleaned_data['cloth']
            quantity = form.cleaned_data['quantity']
            
            # Calculate total purchased quantity
            total_purchased = Expense.objects.filter(cloth_id=cloth_id, user=request.user).aggregate(total=Sum('quantity'))['total'] or 0
            
            # Calculate total sold quantity (including the new one)
            total_sold = Income.objects.filter(cloth_id=cloth_id, user=request.user).aggregate(total=Sum('quantity'))['total'] or 0
            new_total = total_sold + quantity
            
            if new_total > total_purchased:
                form.add_error('quantity', f'Cannot sell {quantity}. Available stock is {total_purchased - total_sold}.')
            else:
                income = form.save(commit=False)
                income.user = request.user
                income.quantity = quantity
                income.save()
                return redirect('income_list')
    else:
        form = IncomeForm(user=request.user)
    return render(request, 'transactions/income_form.html', {
        'form': form,
        'available_cloths': form.fields['cloth'].queryset
    })