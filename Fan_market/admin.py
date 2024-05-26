from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, MainItem, Comment, Cart, CartItem, Company, Dust

admin.site.register(Category)
admin.site.register(Company)
admin.site.register(Dust)
admin.site.register(MainItem)
admin.site.register(Comment)
admin.site.register(Cart)
admin.site.register(CartItem)

