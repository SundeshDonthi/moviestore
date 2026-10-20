from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Report, Review
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from cart.models import Item
from cart.regions import REGIONS
# Create your views here.

def index(request):
    search_term = request.GET.get('search', '')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie, is_removed=False)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, movie__id=id)
    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        Report.objects.create(review=review, reporter=request.user, reason=reason)
        review.is_removed = True
        review.save()
        messages.success(request, "Thank you. The review has been reported and removed from the page.")
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)


@login_required
def popularity_map(request):
    # get the selected region, default to southeast
    selected = request.GET.get('region', 'southeast')

    # check that the region is valid
    if selected not in REGIONS:
        selected = 'southeast'

    # calculate total purchases for each movie in each region
    totals = (
        Item.objects
        .exclude(order__region='')
        .values(
            'order__region',
            'movie_id',
            'movie__name'
        )
        .annotate(purchases=Sum('quantity'))
        .order_by(
            'order__region',
            '-purchases',
            'movie__name',
            'movie_id'
        )
    )

    # store trending movies for each region
    rankings = {
        region: [] for region in REGIONS
    }

    # organize movies into their respective regions
    for row in totals:
        region = row['order__region']

        if region in rankings:
            rankings[region].append({
                'movie_id': row['movie_id'],
                'name': row['movie__name'],
                'count': row['purchases'],
            })

    # create map markers with regional purchase totals
    markers = [
        dict(
            id=key,
            **value,
            total=sum(
                movie['count']
                for movie in rankings[key]
            )
        )
        for key, value in REGIONS.items()
    ]

    # pass map data and trending movies to template
    return render(
        request,
        'movies/popularity_map.html',
        {
            'template_data': {
                'title': 'Local Popularity Map'
            },
            'markers': markers,
            'rankings': rankings,
            'selected': selected,
            'selected_name': REGIONS[selected]['name'],
            'top_movies': rankings[selected],
        }
    )
