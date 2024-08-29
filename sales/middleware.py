from .supabase_client import get_supabase_client

class SupabaseSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'user_id' in request.session:
            supabase = get_supabase_client()
            try:
                # Refresh the session if needed
                supabase.auth.refresh_session()
            except Exception:
                # If refresh fails, clear the session
                del request.session['user_id']
                del request.session['email']

        response = self.get_response(request)
        return response