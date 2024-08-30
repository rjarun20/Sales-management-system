from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from .supabase_client import supabase, get_supabase_client
from django.urls import reverse_lazy
from .models import Client
from django.http import JsonResponse
import random
import string
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def generate_client_id():
    while True:
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))  # Increased to 6 characters
        client_id = f"TSV-LG-CLN-{random_part}"
        
        # Check if this ID already exists
        response = supabase.table('client').select('client_id').eq('client_id', client_id).execute()
        
        if not response.data:
            return client_id  

def test_supabase_connection(request):
    try:
        response = supabase.table('client').select("id").limit(1).execute()
        return JsonResponse({"status": "success", "message": "Connected to Supabase successfully"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)})

class SupabaseLoginRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if 'user_id' not in request.session:
            messages.error(request, "Please log in to access this page.")
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

class LoginView(View):
    template_name = 'sales/login.html'

    def get(self, request):
        if 'user_id' in request.session:
            return redirect('dashboard')
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            supabase = get_supabase_client()
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            user = response.user

            if user:
                request.session['user_id'] = user.id
                request.session['email'] = user.email
                messages.success(request, f"Welcome, {user.email}!")
                return redirect('dashboard')
            else:
                messages.error(request, "Invalid login credentials. Please try again.")
        except Exception as e:
            messages.error(request, f"Login failed: {str(e)}")

        return render(request, self.template_name)

class DashboardView(SupabaseLoginRequiredMixin, View):
    template_name = 'sales/dashboard.html'

    def get(self, request):
        email = request.session.get('email', '')
        user_name = email.split('@')[0] if email else 'User'

        context = {
            'email': email,
            'user_name': user_name,
        }
        return render(request, self.template_name, context)

class ClientListView(SupabaseLoginRequiredMixin, View):
    template_name = 'sales/client_list.html'

    def get(self, request):
        try:
            response = supabase.table('client').select("*").eq("is_deleted", False).execute()
            if response.data:
                clients = [Client(**client) for client in response.data]
            else:
                clients = []
                messages.info(request, "No clients found.")
        except Exception as e:
            clients = []
            messages.error(request, f"Error fetching clients: {str(e)}")

        return render(request, self.template_name, {'clients': clients})

class ClientDetailView(SupabaseLoginRequiredMixin, View):
    template_name = 'sales/client_detail.html'

    def get(self, request, client_id):
        try:
            response = supabase.table('client').select("*").eq("client_id", client_id).execute()
            logger.info(f"Supabase response for client {client_id}: {response.data}")
            
            if response.data:
                client = Client(**response.data[0])
                logger.info(f"Client object: {vars(client)}")
                return render(request, self.template_name, {'client': client})
            else:
                messages.error(request, "Client not found.")
                return redirect('client_list')
        except Exception as e:
            logger.error(f"Error fetching client details: {str(e)}")
            messages.error(request, f"Error fetching client details: {str(e)}")
            return redirect('client_list')

class ClientCreateView(SupabaseLoginRequiredMixin, View):
    template_name = 'sales/client_form.html'

    def get(self, request):
        return render(request, self.template_name, {'client': {}})

    def post(self, request):
        data = {
            'client_id': generate_client_id(),
            'name': request.POST.get('name'),
            'contact_name': request.POST.get('contact_name'),
            'contact_number': request.POST.get('contact_number'),
            'email': request.POST.get('email'),
            'address_line1': request.POST.get('address_line1'),
            'address_line2': request.POST.get('address_line2'),
            'country': request.POST.get('country'),
            'state': request.POST.get('state'),
            'city': request.POST.get('city'),
            'code': request.POST.get('code'),
            'created_by': request.session.get('email'),
            'updated_by': request.session.get('email')
        }
        response = supabase.table('client').insert(data).execute()
        
        if response.data:
            messages.success(request, "Client created successfully.")
            return redirect('client_list')
        else:
            messages.error(request, "Failed to create client.")
            return render(request, self.template_name, {'client': data})

class ClientUpdateView(SupabaseLoginRequiredMixin, View):
    template_name = 'sales/client_form.html'

    def get(self, request, client_id):
        response = supabase.table('client').select("*").eq("client_id", client_id).execute()
        if response.data:
            client = Client(**response.data[0])
            return render(request, self.template_name, {'client': client})
        return redirect('client_list')

    def post(self, request, client_id):
        data = {
            'name': request.POST.get('name'),
            'contact_name': request.POST.get('contact_name'),
            'contact_number': request.POST.get('contact_number'),
            'email': request.POST.get('email'),
            'address_line1': request.POST.get('address_line1'),
            'address_line2': request.POST.get('address_line2'),
            'country': request.POST.get('country'),
            'state': request.POST.get('state'),
            'city': request.POST.get('city'),
            'code': request.POST.get('code'),
            'updated_by': request.session.get('email')
        }
        response = supabase.table('client').update(data).eq("client_id", client_id).execute()
        
        if response.data:
            messages.success(request, "Client updated successfully.")
            return redirect('client_list')
        else:
            messages.error(request, "Failed to update client.")
            return render(request, self.template_name, {'client': data})

class ClientDeleteView(SupabaseLoginRequiredMixin, View):
    template_name = 'sales/client_confirm_delete.html'

    def get(self, request, client_id):
        try:
            response = supabase.table('client').select("*").eq("client_id", client_id).execute()
            if response.data:
                client = Client(**response.data[0])
                return render(request, self.template_name, {'client': client})
            else:
                messages.error(request, "Client not found.")
                return redirect('client_list')
        except Exception as e:
            messages.error(request, f"Error fetching client: {str(e)}")
            return redirect('client_list')

    def post(self, request, client_id):
        try:
            # Instead of deleting, we're setting is_deleted to True
            response = supabase.table('client').update({"is_deleted": True}).eq("client_id", client_id).execute()
            if response.data:
                messages.success(request, "Client successfully deleted.")
            else:
                messages.error(request, "Failed to delete client.")
        except Exception as e:
            messages.error(request, f"Error deleting client: {str(e)}")
        
        return redirect('client_list')

    def post(self, request, client_id):
        response = supabase.table('client').update({"is_deleted": True}).eq("client_id", client_id).execute()
        if response.data:
            messages.success(request, "Client deleted successfully.")
        else:
            messages.error(request, "Failed to delete client.")
        return redirect('client_list')

def logout_view(request):
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_out()
        
        if 'user_id' in request.session:
            del request.session['user_id']
        if 'email' in request.session:
            del request.session['email']
        
        messages.success(request, "You have been successfully logged out.")
    except Exception as e:
        messages.error(request, f"An error occurred during logout: {str(e)}")
    
    return redirect('login')