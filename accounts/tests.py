from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from cart.models import Order, Item
from movies.models import Movie


class AdminDashboardTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user('admin1', password='pw', is_staff=True)
        self.alice = User.objects.create_user('alice', password='pw')
        self.bob = User.objects.create_user('bob', password='pw')
        self.movie = Movie.objects.create(name='Inception', price=10, description='d', image='x.jpg')
        self.url = reverse('accounts.admin_dashboard')

    def buy(self, user, quantity):
        order = Order.objects.create(user=user, total=10 * quantity)
        Item.objects.create(order=order, movie=self.movie, price=10, quantity=quantity)

    def test_regular_user_cannot_view(self):
        self.client.login(username='alice', password='pw')
        self.assertEqual(self.client.get(self.url).status_code, 302)

    def test_shows_top_user_and_updates(self):
        self.buy(self.alice, 2)
        self.client.login(username='admin1', password='pw')
        res = self.client.get(self.url)
        self.assertEqual(res.context['template_data']['top_users'], [self.alice])
        self.assertEqual(res.context['template_data']['top_count'], 2)
        self.buy(self.bob, 5)
        res = self.client.get(self.url)
        self.assertEqual(res.context['template_data']['top_users'], [self.bob])
        self.assertEqual(res.context['template_data']['top_count'], 5)
        self.assertContains(res, 'bob')

    def test_no_purchases(self):
        self.client.login(username='admin1', password='pw')
        self.assertContains(self.client.get(self.url), 'No purchases')