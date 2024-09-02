from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.messages import get_messages
from django.views import View
from .supabase_client import supabase, get_supabase_client
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse_lazy
from .models import Client
from django.http import JsonResponse
import random
import string
from datetime import datetime
import logging
import os
import platform
import time

logger = logging.getLogger(__name__)

# Path to the file storing the last used client ID
LAST_USED_ID_FILE = os.path.join(os.path.dirname(__file__), 'last_used_id.txt')

def read_last_used_id(file):
    try:
        file.seek(0)
        content = file.read().strip()
        if content:
            return int(content)
        else:
            logger.warning("last_used_id.txt is empty. Initializing with default value 999.")
            return 999  # Default value if the file is empty
    except ValueError:
        logger.warning(f"Invalid data in last_used_id.txt: {content}. Initializing with default value 999.")
        return 999  # Default value if the file contains invalid data

def write_last_used_id(file, last_used_id):
    file.seek(0)
    file.truncate()
    file.write(str(last_used_id))
    file.flush()

def lock_file(file):
    if platform.system() == 'Windows':
        import portalocker
        portalocker.lock(file, portalocker.LOCK_EX)
    else:
        import fcntl
        fcntl.flock(file, fcntl.LOCK_EX)

def unlock_file(file):
    if platform.system() == 'Windows':
        import portalocker
        portalocker.unlock(file)
    else:
        import fcntl
        fcntl.flock(file, fcntl.LOCK_UN)


def generate_client_id():
    max_retries = 5
    for attempt in range(max_retries):
        try:
            # Ensure the file exists and is properly initialized
            if not os.path.exists(LAST_USED_ID_FILE):
                with open(LAST_USED_ID_FILE, 'w') as file:
                    file.write('999')

            with open(LAST_USED_ID_FILE, 'r+') as file:
                # Acquire an exclusive lock on the file
                lock_file(file)
                
                # Read the current last used ID
                last_used_id = read_last_used_id(file)
                
                # Increment the last used ID
                new_last_used_id = last_used_id + 1
                
                # Write the new last used ID back to the file
                write_last_used_id(file, new_last_used_id)
                
                # Release the lock
                unlock_file(file)
                
                # Generate the new client ID
                client_id = f"TSV-CHN-CLN-{new_last_used_id:04d}"
                
                return client_id
        except Exception as e:
            logger.error(f"Error generating client ID (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt == max_retries - 1:
                logger.error("Max retries reached. Using fallback client ID.")
                return f"TSV-CHN-CLN-ERR-{random.randint(1000, 9999)}"
            time.sleep(0.1)  # Short delay before retrying

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
            response = supabase.table('client').update({"is_deleted": True}).eq("client_id", client_id).execute()
            if response.data:
                request.session['delete_success_message'] = "Client deleted successfully."
            else:
                request.session['delete_error_message'] = "Failed to delete client."
        except Exception as e:
            request.session['delete_error_message'] = f"Error deleting client: {str(e)}"
        
        return redirect('client_list')

class LoginView(View):
    template_name = 'sales/login.html'

    @method_decorator(csrf_protect)
    def get(self, request):
        # Clear all existing messages
        storage = get_messages(request)
        for message in storage:
            pass  # Iterating through messages marks them as used

        if 'user_id' in request.session:
            return redirect('dashboard')
        return render(request, self.template_name)

    @method_decorator(csrf_protect)
    def post(self, request):
        # Clear all existing messages
        storage = get_messages(request)
        for message in storage:
            pass  # Iterating through messages marks them as used

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

class ClientCreateView(SupabaseLoginRequiredMixin, View):
    template_name = 'sales/client_form.html'

    def get(self, request):
        client_id = generate_client_id()
        return render(request, self.template_name, {'client': {'client_id': client_id}})

    def post(self, request):
        data = {
            'client_id': request.POST.get('client_id'),
            'name': request.POST.get('name'),
            'contact_name': request.POST.get('contact_name'),
            'contact_number': request.POST.get('contact_number'),
            'email': request.POST.get('email'),
            'address_line1': request.POST.get('address_line1'),
            'address_line2': request.POST.get('address_line2'),
            'country': request.POST.get('country', 'India'),  # Default to 'India' if not in POST data
            'state': request.POST.get('state'),
            'city': request.POST.get('city'),
            'code': request.POST.get('code'),
            'created_by': request.session.get('email'),
            'updated_by': request.session.get('email')
        }

        # Validate required fields
        required_fields = ['client_id', 'name', 'contact_name', 'contact_number', 'email', 'address_line1', 'country', 'state', 'city', 'code']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            messages.error(request, f"The following fields are required: {', '.join(missing_fields)}")
            return render(request, self.template_name, {'client': data})

        try:
            response = supabase.table('client').insert(data).execute()
            
            if response.data:
                messages.success(request, "Client created successfully.")
                return redirect('client_list')
            else:
                messages.error(request, "Failed to create client. Please try again.")
        except Exception as e:
            messages.error(request, f"An error occurred while creating the client: {str(e)}")
        
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
            'client_id': client_id,
            'name': request.POST.get('name'),
            'contact_name': request.POST.get('contact_name'),
            'contact_number': request.POST.get('contact_number'),
            'email': request.POST.get('email'),
            'address_line1': request.POST.get('address_line1'),
            'address_line2': request.POST.get('address_line2'),
            'country': request.POST.get('country') or 'India',
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

            # Check for messages in the session
            if 'delete_success_message' in request.session:
                messages.success(request, request.session['delete_success_message'])
                del request.session['delete_success_message']
            elif 'delete_error_message' in request.session:
                messages.error(request, request.session['delete_error_message'])
                del request.session['delete_error_message']

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

def logout_view(request):
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_out()
        
        if 'user_id' in request.session:
            del request.session['user_id']
        if 'email' in request.session:
            del request.session['email']
        
        # Clear all existing messages
        storage = get_messages(request)
        for message in storage:
            pass  # Iterating through messages marks them as used
        
        messages.success(request, "You have been successfully logged out.")
    except Exception as e:
        messages.error(request, f"An error occurred during logout: {str(e)}")
    
    return redirect('login')