from django.shortcuts import render
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from .forms import CustomUserCreationForm, CustomErrorList
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required 
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from cart.models import Item
from movies.models import Movie, Review
# Create your views here.
def signup(request):
    template_data = {}
    template_data['title'] = 'Sign Up'
    if request.method == 'GET':
        template_data['form'] = CustomUserCreationForm()
        return render(request, 'accounts/signup.html', {'template_data': template_data})
    elif request.method == 'POST':
        form = CustomUserCreationForm(request.POST, error_class=CustomErrorList)
        if form.is_valid():
            form.save()
            return redirect('accounts.login')
        else:
            template_data['form'] = form
            return render(request, 'accounts/signup.html', {'template_data': template_data})
def logout(request):
    auth_logout(request)
    return redirect('home.index')
def login(request):
    template_data = {}
    template_data['title'] = 'Login'
    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'template_data': template_data})
    elif request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            template_data['error'] = 'The username or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})
        else:
            auth_login(request, user)
            return redirect('home.index')

@login_required
def orders(request):
    template_data = {}
    template_data['title'] = 'Orders'
    template_data['orders'] = request.user.order_set.all()
    return render(request, 'accounts/orders.html',
        {'template_data': template_data})

@staff_member_required(login_url='accounts.login')
def admin_dashboard(request):
    purchasers = (
        User.objects.filter(order__isnull=False)

    .annotate(movies_purchased=Sum('order__item__quantity'))
    .order_by('-movies_purchased', 'username')
    )
    all_reviews = Review.objects.all()
    movie_review_counts = {}
    max_review_count = 0
    max_review_movie = Review
    for review in all_reviews:
        if review.movie not in movie_review_counts:
            movie_review_counts[review] = 1
        else:
            movie_review_counts[review] += 1
        if movie_review_counts[review] > max_review_count:
            max_review_count = movie_review_counts[review]
            max_review_movie = review
            
    top_count = purchasers[0].movies_purchased if purchasers else 0
    top_users = [u for u in purchasers if u.movies_purchased == top_count]
    template_data = {}
    template_data['title'] = 'Admin Dashboard'
    template_data['top_users'] = top_users
    template_data['top_count'] = top_count
    template_data['purchasers'] = purchasers

    template_data['top_purchases'] = [
        (u, Item.objects.filter(order__user=u)
         .values('movie__name')
         .annotate(quantity=Sum('quantity'))
         .order_by('-quantity', 'movie__name'))
         for u in top_users
    ]

    content = {
        'template_data' : template_data,
        'max_review_movie' : max_review_movie
    }

    return render(request, 'accounts/admin_dashboard.html', content)