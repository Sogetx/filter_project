from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("", views.index, name="index"),
    path('filter/', views.items_filter, name='filter'),
    path('signout/', views.signout, name='signout'),
    path('configurator/', views.configurator, name='configurator'),
    path('configurator/<int:category_id>/', views.configurator_by_category, name='configurator_by_category'),
    path('products/', views.index, name='products'),
    path('<int:pk>/', views.show_details, name='detail'),
    path('add_to_cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('update_cart_item_quantity/', views.update_cart_item_quantity, name='update_cart_item_quantity'),
    path('account_info/', views.account_view, name='account_info'),
    path('account_info/change_name/', views.account_change_name, name='account_change_name'),
    path('account/change-email/', views.account_change_email, name='account_change_email'),
    path('reply_to_comment/<int:comment_id>/', views.reply_to_comment, name='reply_to_comment'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('order_pdf/', views.order_pdf, name='order_pdf'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


