
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from PIL import Image
from django.db.models.signals import post_save
from django.dispatch import receiver


# Products BLOCK
class Category(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Сompanies"

    def __str__(self):
        return self.name


class Dust(models.Model):
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ('name',)
        verbose_name_plural = "Dust Types"

    def __str__(self):
        return self.name


class MainItem(models.Model):
    name = models.CharField(max_length=200, default="Product!")
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0,
                                validators=[MinValueValidator(0), MaxValueValidator(999.99)])
    description = models.TextField(default="Hello World!")
    creat_by = models.ForeignKey(User, related_name='item', on_delete=models.CASCADE)
    creat_at = models.DateTimeField(auto_now_add=True)
    # image = models.CharField(max_length=5000, default="./images/1.png", blank=True)
    image = models.ImageField(upload_to='templates/web_view/images/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    dust = models.ManyToManyField(Dust)
    min_particle_size = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    max_particle_size = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cleaning_efficiency = models.IntegerField(null=True, blank=True)
    temperature = models.IntegerField(null=True, blank=True)
    concentration = models.IntegerField(null=True, blank=True)

    @property
    def average_rating(self):
        total_rating = sum(comment.rating for comment in self.comments.all())
        total_comments = self.comments.count()
        return total_rating / total_comments if total_comments != 0 else 0

    def __str__(self):
        return f"{self.name}: {self.price}: due {self.description} {self.image}"


# CART BLOCK
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    items = models.ManyToManyField('MainItem', through='CartItem')


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    item = models.ForeignKey(MainItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


# COMMENTS BLOCK
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(MainItem, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(6)])
    created_at = models.DateTimeField(auto_now_add=True)

    #rating = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']


class Reply(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    def __str__(self):
        return f'Reply by {self.user.username} on {self.comment.item.name}'


# IMAGE AUTO-CROP
@receiver(post_save, sender=MainItem)
def auto_crop_images(sender, instance, **kwargs):
    if instance.image:
        image_path = instance.image.path
        img = Image.open(image_path)
        img.thumbnail((900, 800))
        img.save(image_path)
