from django.urls import path
from .views import (
    LoginView, DashboardView, ClientListView, ClientDetailView,
    ClientCreateView, ClientUpdateView, ClientDeleteView, test_supabase_connection, logout_view
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/create/', ClientCreateView.as_view(), name='client_create'),
    path('clients/<str:client_id>/', ClientDetailView.as_view(), name='client_detail'),
    path('clients/<str:client_id>/update/', ClientUpdateView.as_view(), name='client_update'),
    path('clients/<str:client_id>/delete/', ClientDeleteView.as_view(), name='client_delete'),
    path('test-supabase/', test_supabase_connection, name='test_supabase'),
]