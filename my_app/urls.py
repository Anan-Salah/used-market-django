from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('add-item/', views.add_item, name='add_item'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('register/', views.register_view, name='register'),
    path('edit-item/<int:item_id>/', views.edit_item, name='edit_item'),
    path('logout/', views.logout_view, name='logout'),
    path('delete-item/<int:item_id>/', views.delete_item, name='delete_item'),
    path('account/', views.account_view, name='account'),




]
