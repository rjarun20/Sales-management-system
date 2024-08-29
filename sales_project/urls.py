from django.contrib import admin
from django.urls import path, include
from sales.views import LoginView, DashboardView
from django.shortcuts import redirect

# Function to redirect root URL to login page
def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('', redirect_to_login, name='home'),
    path('clients/', include('sales.urls')),
]