from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from transactions.models import Expense, Income
from django.db.models import Sum, Count, Q, Case, When, Value, IntegerField, FloatField, DecimalField
from django.db.models.functions import Coalesce, TruncMonth, TruncDay
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle  # Added for table formatting
from reportlab.lib import colors
from openpyxl import Workbook
from io import BytesIO
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import timedelta
from django.utils import timezone
import csv

@login_required
def dashboard(request):
    period = request.GET.get('period', 'month')
    today = timezone.now().date()
    expenses = Expense.objects.filter(user=request.user, date__gte=today - timedelta(days=365))  # Last 12 months
    incomes = Income.objects.filter(user=request.user, date__gte=today - timedelta(days=365))

    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_incomes = incomes.aggregate(total=Sum('amount'))['total'] or 0

    # Category aggregations for pie charts
    expense_data = expenses.values('cloth__subcategory__category__name').annotate(total=Sum('amount')).order_by('cloth__subcategory__category__name')
    income_data = incomes.values('cloth__subcategory__category__name').annotate(total=Sum('amount')).order_by('cloth__subcategory__category__name')
    expense_labels = [item['cloth__subcategory__category__name'] for item in expense_data]
    expense_amounts = [float(item['total']) for item in expense_data]
    income_labels = [item['cloth__subcategory__category__name'] for item in income_data]
    income_amounts = [float(item['total']) for item in income_data]

    # Data for Overall Expenses by Category (bar chart)
    expense_dict = {item['cloth__subcategory__category__name']: float(item['total']) for item in expense_data}
    income_dict = {item['cloth__subcategory__category__name']: float(item['total']) for item in income_data}
    all_categories = sorted(list(set(expense_labels + income_labels)))
    expense_amounts_full = [expense_dict.get(cat, 0) for cat in all_categories]
    income_amounts_full = [income_dict.get(cat, 0) for cat in all_categories]
    profit_amounts = [income_dict.get(cat, 0) - expense_dict.get(cat, 0) for cat in all_categories]

    # Subcategory data
    if period == 'day':
        expense_sub_data = expenses.values('cloth__subcategory__name', 'date').annotate(total=Sum('amount')).order_by('cloth__subcategory__category__name', 'date')
        income_sub_data = incomes.values('cloth__subcategory__name', 'date').annotate(total=Sum('amount')).order_by('cloth__subcategory__category__name', 'date')
    else:
        expense_sub_data = expenses.values('cloth__subcategory__name').annotate(total=Sum('amount')).order_by('cloth__subcategory__name')
        income_sub_data = incomes.values('cloth__subcategory__name').annotate(total=Sum('amount')).order_by('cloth__subcategory__name')

    sub_labels = list(set(
        [item['cloth__subcategory__name'] for item in expense_sub_data] +
        [item['cloth__subcategory__name'] for item in income_sub_data]
    ))
    expense_sub_dict = {item['cloth__subcategory__name']: float(item['total']) for item in expense_sub_data}
    income_sub_dict = {item['cloth__subcategory__name']: float(item['total']) for item in income_sub_data}
    expense_sub_amounts = [expense_sub_dict.get(label, 0) for label in sub_labels]
    income_sub_amounts = [income_sub_dict.get(label, 0) for label in sub_labels]
    profit_sub_amounts = [income_sub_dict.get(label, 0) - expense_sub_dict.get(label, 0) for label in sub_labels]

    # Cloth frequency and amount data (time series for differences over last 12 months)
    if period == 'day':
        cloth_freq_expense_data = expenses.values('cloth__name', 'date').annotate(
            count=Coalesce(Count('id'), Value(0), output_field=IntegerField())
        ).order_by('date')
        cloth_freq_income_data = incomes.values('cloth__name', 'date').annotate(
            count=Coalesce(Count('id'), Value(0), output_field=IntegerField())
        ).order_by('date')
        cloth_amount_expense_data = expenses.values('cloth__name', 'date').annotate(
            total=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
        ).order_by('date')
        cloth_amount_income_data = incomes.values('cloth__name', 'date').annotate(
            total=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
        ).order_by('date')
        time_labels = [d.strftime('%Y-%m-%d') for d in [today - timedelta(days=i) for i in range(365, -1, -1)]]
    else:
        cloth_freq_expense_data = expenses.annotate(month=TruncMonth('date')).values('cloth__name', 'month').annotate(
            count=Coalesce(Count('id'), Value(0), output_field=IntegerField())
        ).order_by('month')
        cloth_freq_income_data = incomes.annotate(month=TruncMonth('date')).values('cloth__name', 'month').annotate(
            count=Coalesce(Count('id'), Value(0), output_field=IntegerField())
        ).order_by('month')
        cloth_amount_expense_data = expenses.annotate(month=TruncMonth('date')).values('cloth__name', 'month').annotate(
            total=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
        ).order_by('month')
        cloth_amount_income_data = incomes.annotate(month=TruncMonth('date')).values('cloth__name', 'month').annotate(
            total=Coalesce(Sum('amount'), Value(0), output_field=DecimalField())
        ).order_by('month')
        time_labels = sorted(list(set(
            [item['month'].strftime('%Y-%m') for item in cloth_freq_expense_data] +
            [item['month'].strftime('%Y-%m') for item in cloth_freq_income_data]
        )))
        # Ensure all 12 months are included, even with no data
        start_month = (today.replace(day=1) - timedelta(days=365)).strftime('%Y-%m')
        time_labels = sorted([start_month] + [d.strftime('%Y-%m') for d in [today.replace(day=1) - timedelta(days=30*i) for i in range(11, -1, -1)]])

    # Lookup dictionaries
    frequency_expense_lookup = {
        (item['cloth__name'], item['date'].strftime('%Y-%m-%d') if period == 'day' else item['month'].strftime('%Y-%m')): item['count']
        for item in cloth_freq_expense_data
    }
    frequency_income_lookup = {
        (item['cloth__name'], item['date'].strftime('%Y-%m-%d') if period == 'day' else item['month'].strftime('%Y-%m')): item['count']
        for item in cloth_freq_income_data
    }
    amount_expense_lookup = {
        (item['cloth__name'], item['date'].strftime('%Y-%m-%d') if period == 'day' else item['month'].strftime('%Y-%m')): float(item['total'])
        for item in cloth_amount_expense_data
    }
    amount_income_lookup = {
        (item['cloth__name'], item['date'].strftime('%Y-%m-%d') if period == 'day' else item['month'].strftime('%Y-%m')): float(item['total'])
        for item in cloth_amount_income_data
    }

    # Only include cloths used in expenses
    cloth_names = sorted(list(set(item['cloth__name'] for item in cloth_freq_expense_data if item['cloth__name'])))
    colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']

    cloth_frequency_datasets = []
    cloth_amount_datasets = []

    for i, cloth in enumerate(cloth_names):
        # Frequency difference (Incomes - Expenses) for each time period
        freq_diff_data = []
        for time in time_labels:
            income_count = frequency_income_lookup.get((cloth, time), 0)
            expense_count = frequency_expense_lookup.get((cloth, time), 0)
            freq_diff_data.append(income_count - expense_count)

        # Amount difference (Incomes - Expenses) for each time period
        amount_diff_data = []
        for time in time_labels:
            income_amount = amount_income_lookup.get((cloth, time), 0)
            expense_amount = amount_expense_lookup.get((cloth, time), 0)
            amount_diff_data.append(income_amount - expense_amount)

        # Frequency dataset (Difference: Incomes - Expenses)
        cloth_frequency_datasets.append({
            'label': f'{cloth} Difference (Inc - Exp)',
            'data': freq_diff_data,
            'borderColor': colors[i % len(colors)],
            'borderDash': [],
            'fill': False
        })

        # Amount dataset (Difference: Incomes - Expenses)
        cloth_amount_datasets.append({
            'label': f'{cloth} Difference (Inc - Exp)',
            'data': amount_diff_data,
            'borderColor': colors[i % len(colors)],
            'borderDash': [],
            'fill': False
        })

    # Radar Chart - Cloth Profit, Expense, and Income Trends
    cloth_profit_labels = []
    cloth_expense_data = []
    cloth_income_data = []
    cloth_profit_data = []
    if expenses.exists() or incomes.exists():
        cloths = sorted(list(set(
            exp.cloth.name for exp in expenses if exp.cloth
        ) | set(
            inc.cloth.name for inc in incomes if inc.cloth
        )))
        cloth_profit_labels = cloths
        for cloth in cloths:
            income_sum = incomes.filter(cloth__name=cloth).aggregate(total=Sum('amount'))['total'] or 0
            expense_sum = expenses.filter(cloth__name=cloth).aggregate(total=Sum('amount'))['total'] or 0
            profit = float(income_sum) - float(expense_sum)
            cloth_income_data.append(float(income_sum))
            cloth_expense_data.append(float(expense_sum))
            cloth_profit_data.append(profit)

    context = {
        'total_expenses': json.dumps(float(total_expenses)),
        'total_incomes': json.dumps(float(total_incomes)),
        'expense_labels': json.dumps(expense_labels),
        'expense_data': json.dumps(expense_amounts),
        'income_labels': json.dumps(income_labels),
        'income_data': json.dumps(income_amounts),
        'all_categories': json.dumps(all_categories),
        'expense_amounts_full': json.dumps(expense_amounts_full),
        'income_amounts_full': json.dumps(income_amounts_full),
        'profit_amounts': json.dumps(profit_amounts),
        'sub_labels': json.dumps(sub_labels),
        'expense_sub_data': json.dumps(expense_sub_amounts),
        'income_sub_data': json.dumps(income_sub_amounts),
        'profit_sub_amounts': json.dumps(profit_sub_amounts),
        'time_labels': json.dumps(time_labels),
        'cloth_frequency_datasets': json.dumps(cloth_frequency_datasets),
        'cloth_amount_datasets': json.dumps(cloth_amount_datasets),
        'period': period,
        'cloth_profit_labels': json.dumps(cloth_profit_labels),  # cloth names
        'cloth_expense_data': json.dumps(cloth_expense_data),    # expense values
        'cloth_income_data': json.dumps(cloth_income_data),      # income values
        'cloth_profit_data': json.dumps(cloth_profit_data),      # profit values
    }

    return render(request, 'dashboard/dashboard.html', context)

@login_required
def download_report(request, format_type):
    period = request.GET.get('period', 'month')
    expenses = Expense.objects.filter(user=request.user)
    incomes = Income.objects.filter(user=request.user)

    if format_type == 'jpg':
        fig, ax = plt.subplots()
        categories = expenses.values('cloth__subcategory__category__name').annotate(total=Sum('amount')).order_by('cloth__subcategory__category__name')
        labels = [item['cloth__subcategory__category__name'] for item in categories]
        amounts = [float(item['total']) for item in categories]
        ax.pie(amounts, labels=labels, autopct='%1.1f%%')
        ax.set_title('Expenses by Category')
        buffer = BytesIO()
        plt.savefig(buffer, format='jpg')
        plt.close()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='image/jpeg')
        response['Content-Disposition'] = 'attachment; filename="report.jpg"'
        return response

    elif format_type == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Type', 'Shop', 'Category', 'Subcategory', 'Cloth', 'Amount', 'Date'])
        for expense in expenses:
            writer.writerow(['Expense', expense.shop.name, expense.cloth.subcategory.category.name, 
                           expense.cloth.subcategory.name, expense.cloth.name, expense.amount, 
                           expense.date.strftime('%Y-%m-%d')])
        for income in incomes:
            writer.writerow(['Income', income.shop.name, income.cloth.subcategory.category.name, 
                           income.cloth.subcategory.name, income.cloth.name, income.amount, 
                           income.date.strftime('%Y-%m-%d')])
        return response

    elif format_type == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="report.pdf"'
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        data = [['Type', 'Shop', 'Category', 'Subcategory', 'Cloth', 'Amount', 'Date']]
        for expense in expenses:
            data.append(['Expense', expense.shop.name, expense.cloth.subcategory.category.name, 
                        expense.cloth.subcategory.name, expense.cloth.name, str(expense.amount), 
                        expense.date.strftime('%Y-%m-%d')])
        for income in incomes:
            data.append(['Income', income.shop.name, income.cloth.subcategory.category.name, 
                        income.cloth.subcategory.name, income.cloth.name, str(income.amount), 
                        income.date.strftime('%Y-%m-%d')])
        table = Table(data)
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
        table.setStyle(style)
        elements = [table]
        doc.build(elements)
        response.write(buffer.getvalue())
        buffer.close()
        return response