from supabase import create_client, Client
from django.conf import settings

supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_supabase_client():
    global supabase
    return supabase

def initialize_supabase():
    global supabase
    supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

# Call this function when you want to reinitialize the Supabase client
# initialize_supabase()