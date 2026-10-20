from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from movies.models import Movie
from cart.models import Order, Item



# Create your tests here.

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from movies.models import Movie
from cart.models import Order, Item


class PopularityMapTests(TestCase):

    def setUp(self):
        # create a test user and log them in
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        self.client.login(
            username='testuser',
            password='testpassword123'
        )

        # create a test movie
        self.movie = Movie.objects.create(
            name='Test Movie',
            price=10,
            description='Test description'
        )

        # create a purchase in the southeast region
        self.order = Order.objects.create(
            user=self.user,
            total=30,
            region='southeast'
        )

        # add three purchased copies of the movie
        Item.objects.create(
            order=self.order,
            movie=self.movie,
            quantity=3,
            price=10
        )

    def test_popularity_map_loads(self):
        # check that logged in users can access the map
        response = self.client.get(
            reverse('movies.popularity')
        )

        self.assertEqual(response.status_code, 200)

    def test_movie_purchase_count(self):
        # check that purchases are counted in the correct region
        response = self.client.get(
            reverse('movies.popularity'),
            {'region': 'southeast'}
        )

        top_movies = response.context['top_movies']

        self.assertEqual(len(top_movies), 1)
        self.assertEqual(top_movies[0]['count'], 3)

    def test_other_region_has_no_purchases(self):
        # check that purchases from other regions are not included
        response = self.client.get(
            reverse('movies.popularity'),
            {'region': 'northeast'}
        )

        top_movies = response.context['top_movies']

        self.assertEqual(len(top_movies), 0)

    def test_login_required(self):
        # check that users must log in to view the map
        self.client.logout()

        response = self.client.get(
            reverse('movies.popularity')
        )

        self.assertEqual(response.status_code, 302)
