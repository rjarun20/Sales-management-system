from django.urls import path
from . import views

urlpatterns = [
    path('', views.ClientListView.as_view(), name='client_list'),
    path('create/', views.ClientCreateView.as_view(), name='client_create'),
    path('<str:client_id>/', views.ClientDetailView.as_view(), name='client_detail'),
    path('<str:client_id>/update/', views.ClientUpdateView.as_view(), name='client_update'),
    path('<str:client_id>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),
    path('logout/', views.logout_view, name='logout'),
    path('test-supabase/', views.test_supabase_connection, name='test_supabase'),
]