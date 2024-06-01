from django.test import TestCase, Client

# Create your tests here.
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Category, Company, Dust, MainItem, Comment, Cart, CartItem
from django.core.files.uploadedfile import SimpleUploadedFile
from .conf_forms import ConfForm
from PIL import Image  # for creating item images
import io


# Models TEST
class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Test Category')
        self.assertEqual(str(self.category), 'Test Category')


class CompanyModelTest(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Test Company')

    def test_company_creation(self):
        self.assertEqual(self.company.name, 'Test Company')
        self.assertEqual(str(self.company), 'Test Company')


class DustModelTest(TestCase):
    def setUp(self):
        self.dust = Dust.objects.create(name='Test Dust')

    def test_dust_creation(self):
        self.assertEqual(self.dust.name, 'Test Dust')
        self.assertEqual(str(self.dust), 'Test Dust')


class MainItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='1234567')
        self.category = Category.objects.create(name='Test Category')
        self.company = Company.objects.create(name='Test Company')
        self.dust = Dust.objects.create(name='Test Dust')

        self.main_item = MainItem.objects.create(
            name='Test Item',
            price=10.00,
            description='Test Description',
            creat_by=self.user,
            category=self.category,
            company=self.company,
        )
        self.main_item.dust.add(self.dust)

    def test_main_item_creation(self):
        self.assertEqual(self.main_item.name, 'Test Item')
        self.assertEqual(self.main_item.price, 10.00)
        self.assertEqual(self.main_item.description, 'Test Description')
        self.assertEqual(self.main_item.creat_by, self.user)
        self.assertEqual(self.main_item.category, self.category)
        self.assertEqual(self.main_item.company, self.company)
        self.assertIn(self.dust, self.main_item.dust.all())

    def test_average_rating(self):
        Comment.objects.create(user=self.user, item=self.main_item, text='Good', rating=4)
        Comment.objects.create(user=self.user, item=self.main_item, text='Bad', rating=2)
        self.assertEqual(self.main_item.average_rating, 3.0)


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='1234567')
        self.category = Category.objects.create(name='Test Category')
        self.company = Company.objects.create(name='Test Company')
        self.dust = Dust.objects.create(name='Test Dust')
        self.main_item = MainItem.objects.create(
            name='Test Item',
            price=10.00,
            description='Test Description',
            creat_by=self.user,
            category=self.category,
            company=self.company,
        )
        self.main_item.dust.add(self.dust)
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_creation(self):
        self.assertEqual(self.cart.user, self.user)

    def test_cart_item_creation(self):
        cart_item = CartItem.objects.create(cart=self.cart, item=self.main_item, quantity=2)
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.item, self.main_item)
        self.assertEqual(cart_item.quantity, 2)


# Authentication test
class UserAuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='correct_password')

    def test_correct_password_login(self):
        logged_in = self.client.login(username='testuser', password='correct_password')
        self.assertTrue(logged_in)

    def test_incorrect_password_login(self):
        #self.client.login(username='testuser', password='wrong_password')
        logged_in = self.client.login(username='testuser', password='wrong_password')
        self.assertFalse(logged_in)


# View TEST
class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@example.com', first_name='Petro', last_name='Solony', password='12345678')
        self.client.login(username='testuser', password='12345678')
        self.category = Category.objects.create(name='Test Category')
        self.company = Company.objects.create(name='Test Company')
        self.dust = Dust.objects.create(name='Test Dust')

        # Creating image
        image = Image.new('RGB', (100, 100), color='red')
        byte_arr = io.BytesIO()
        image.save(byte_arr, format='JPEG')
        byte_arr.seek(0)
        self.image = SimpleUploadedFile(name='test_image.jpg', content=byte_arr.read(), content_type='image/jpeg')

        self.main_item = MainItem.objects.create(
            name='Test Item',
            price=10.00,
            description='Test Description',
            creat_by=self.user,
            category=self.category,
            company=self.company,
            image=self.image,
            temperature=100,
            min_particle_size=40.00,
            max_particle_size=999.00,
            cleaning_efficiency=90,
            concentration=50
        )
        self.main_item.dust.add(self.dust)

        self.cart = Cart.objects.create(user=self.user)

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_view/home.html')

    def test_signout_view(self):
        response = self.client.get(reverse('signout'))
        self.assertEqual(response.status_code, 302)  # redirect check

    def test_account_view(self):
        response = self.client.get(reverse('account_info'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_view/account_info.html')

    # PRODUCT BLOCK
    def test_show_details_view(self):
        response = self.client.get(reverse('detail', args=[self.main_item.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_view/details.html')

    # FILTER SEARCH BLOCK
    def test_items_filter_view(self):
        response = self.client.get(reverse('filter'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_view/filter.html')

    def test_items_filter_with_parameters(self):
        response = self.client.get(reverse('filter'), {
            'temperature': 50,
            'min_particle_size': 40.00,
            'max_particle_size': 999.00,
            'cleaning_efficiency': 90,
            'concentration': 50,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_view/filter.html')

        # Compare results
        items = response.context['items']
        self.assertTrue(any(item.pk == self.main_item.pk for item in items))

    def test_items_filter_with_wrong_parameters(self):
        response = self.client.get(reverse('filter'), {
            'temperature': 1500,
            'min_particle_size': -4.00,
            'max_particle_size': 999.00,
            'cleaning_efficiency': 110,
            'concentration': 2000,
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_view/filter.html')

        # Compare results
        items = response.context['items']
        self.assertFalse(any(item.pk == self.main_item.pk for item in items))

    # CART BLOCK
    def test_view_cart(self):
        response = self.client.get(reverse('cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_view/cart.html')

    def test_add_to_cart_view(self):
        response = self.client.post(reverse('add_to_cart', args=[self.main_item.pk]))
        self.assertEqual(response.status_code, 302)  # redirect check

        # Check if item is added to cart
        self.assertTrue(CartItem.objects.filter(cart=self.cart, item=self.main_item).exists())

    def test_remove_from_cart(self):
        # Add item to the cart
        cart_item = CartItem.objects.create(cart=self.cart, item=self.main_item)
        response = self.client.post(reverse('remove_from_cart', args=[cart_item.pk]))
        self.assertEqual(response.status_code, 302)  # redirect check
        # Check remove CartItem
        self.assertFalse(CartItem.objects.filter(cart=self.cart, item=self.main_item).exists())

    # COMMENT BLOCK
    def test_add_comment_from_details_view(self):
        # Comment Data
        form_data = {
            'text': 'Test Comment',
            'rating': '5',
        }

        response = self.client.post(reverse('detail', args=[self.main_item.pk]), form_data)
        self.assertEqual(response.status_code, 302)  # redirect check

        self.assertTrue(Comment.objects.filter(text='Test Comment').exists())

    def test_delete_comment_from_detail_view(self):
        # Grant User Staff_Access for delete comments
        self.user.is_staff = True
        self.user.save()
        # Create comment
        comment = Comment.objects.create(user=self.user, item=self.main_item, text='Test Comment', rating=5)

        response = self.client.post(reverse('delete_comment', args=[comment.pk]))
        self.assertEqual(response.status_code, 302)  # Check redirection

        # Check if comment was deleted
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_reply_to_comment(self):
        # Create comment
        comment = Comment.objects.create(user=self.user, item=self.main_item, text='Test Comment', rating=5)
        response = self.client.post(reverse('reply_to_comment', args=[comment.pk]), {'text': 'Test Answer'})
        self.assertEqual(response.status_code, 302)  # Check redirection
        # Check if reply was added
        self.assertTrue(comment.replies.filter(text='Test Answer').exists())

    def test_delete_reply(self):
        comment = Comment.objects.create(user=self.user, item=self.main_item, text='Test Comment', rating=5)
        reply = comment.replies.create(user=self.user, comment=comment, text='Test Answer fo Delete')

        response = self.client.post(reverse('delete_reply', args=[reply.pk]))
        self.assertEqual(response.status_code, 302)

        self.assertFalse(comment.replies.filter(pk=reply.pk).exists())

    # ACCOUNT VIEWS BLOCK
    def test_account_change_name(self):
        new_first_name = 'Anton'
        new_last_name = 'Petrenko'
        response = self.client.post(reverse('account_change_name'), {'first_name': new_first_name, 'last_name': new_last_name})
        self.assertEqual(response.status_code, 302)  # Redirect to account_info view

        # Refresh the user instance from the database to check changes
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, new_first_name)
        self.assertEqual(self.user.last_name, new_last_name)

    def test_account_change_email(self):
        new_email = 'new_email@example.com'
        response = self.client.post(reverse('account_change_email'), {'email': new_email})
        self.assertEqual(response.status_code, 302)  # Redirect to account_info view

        # Refresh the user instance from the database to check changes
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, new_email)

    def test_account_change_password(self):
        new_password = 'new_password'
        response = self.client.post(reverse('account_change_password'), {'oldpassword': '12345678', 'password1': new_password, 'password2': new_password})
        self.assertEqual(response.status_code, 302)  # Redirect to account_info view

        # Refresh the user instance from the database
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))


# Configurator Test(for clear result it will be separate class)
class ConfiguratorTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345678')
        self.client.login(username='testuser', password='12345678')
        self.category = Category.objects.create(name='Test Category')
        self.company = Company.objects.create(name='Test Company')
        self.dust = Dust.objects.create(name='Test Dust')

        # Creating image
        image = Image.new('RGB', (100, 100), color='red')
        byte_arr = io.BytesIO()
        image.save(byte_arr, format='JPEG')
        byte_arr.seek(0)
        self.image = SimpleUploadedFile(name='test_image.jpg', content=byte_arr.read(), content_type='image/jpeg')

        self.main_item = MainItem.objects.create(
            name='Test Item',
            price=10.00,
            description='Test Description',
            creat_by=self.user,
            category=self.category,
            company=self.company,
            image=self.image,
            temperature=100,
            min_particle_size=40.00,
            max_particle_size=999.00,
            cleaning_efficiency=90,
            concentration=50
        )
        self.main_item.dust.add(self.dust)

        self.cart = Cart.objects.create(user=self.user)

    # CONFIGURATOR BLOCK
    def test_configurator_view(self):
        response = self.client.get(reverse('configurator'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_view/configurator.html')

    def test_configurator_form_with_parameters(self):
        # Choose existing data for form
        form_data = {
            'particle_size': '40-999',
            'cleaning_efficiency': '50',
            'temperature': '50',
            'concentration': '15',
            'dusts': [self.dust.id]
        }

        # Sending form data, check page is open
        response = self.client.post(reverse('configurator'), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_view/configurator.html')

        # Check context for categories, items
        self.assertIn('categories', response.context)
        self.assertIn('items', response.context)
        # Compare results
        categories = response.context['categories']
        items = response.context['items']

        self.assertTrue(any(item.pk == self.main_item.pk for item in items))
        self.assertTrue(any(category.pk == self.category.pk for category in categories))

    def test_configurator_form_with_wrong_parameters(self):
        # Choose non-existing data for form
        form_data = {
            'particle_size': '800-999',
            'cleaning_efficiency': '40',
            'temperature': '1',
            'concentration': '0',
            'dusts': [self.dust.id]
        }

        # Sending form data, check page is open
        response = self.client.post(reverse('configurator'), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'web_view/configurator.html')

        # Check context for categories, items
        self.assertNotIn('categories', response.context)
        self.assertNotIn('items', response.context)
