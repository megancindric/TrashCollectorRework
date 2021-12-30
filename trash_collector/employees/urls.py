from django.urls import path

from . import views

# TODO: Determine what distinct pages are required for the customer user stories, add a path for each in urlpatterns

app_name = "employees"
urlpatterns = [
    path('', views.index, name="index"),
    path('create/', views.create, name='create'),
    path('my_accounts/', views.my_accounts, name='my_accounts'),
    path('confirm_pickup/<int:customer_id>/', views.confirm_pickup, name='confirm_pickup'),
    path('<int:customer_id>/profile/', views.customer_profile, name="customer_profile"),
    path('edit_profile/', views.edit_profile, name="edit_profile")
]