from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from .models import Product
from django.shortcuts import get_object_or_404
from .models import Product, Review
from django.contrib.auth.decorators import login_required


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'store/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
    return render(request, 'store/profile.html', {'u_form': u_form})


def product_list(request):
    products = Product.objects.all()
    size = request.GET.get('size')
    color = request.GET.get('color')
    sort_by = request.GET.get('sort_by')

    if size:
        products = products.filter(size=size)
    if color:
        products = products.filter(color=color)
    if sort_by:
        products = products.order_by(sort_by)

    context = {
        'products': products
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)
    average_rating = reviews.aggregate(models.Avg('rating'))[
        'rating__avg'] or 0

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if rating and comment:
            review = Review(product=product, user=request.user,
                            rating=rating, comment=comment)
            review.save()
            return redirect('product_detail', product_id=product.id)

    context = {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating
    }
    return render(request, 'store/product_detail.html', context)


@login_required
def wishlist(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        if product in wishlist.products.all():
            wishlist.products.remove(product)
        else:
            wishlist.products.add(product)
        return redirect('wishlist')

    context = {
        'wishlist': wishlist
    }
    return render(request, 'store/wishlist.html', context)
