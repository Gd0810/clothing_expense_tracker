from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Shop
from .forms import ShopForm

@login_required
def shop_list(request):
    shops = Shop.objects.filter(user=request.user)
    return render(request, 'shops/shop_list.html', {'shops': shops})

@login_required
def shop_create(request):
    if request.method == 'POST':
        form = ShopForm(request.POST)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.user = request.user
            shop.save()
            return redirect('shop_list')
    else:
        form = ShopForm()
    return render(request, 'shops/shop_form.html', {'form': form})