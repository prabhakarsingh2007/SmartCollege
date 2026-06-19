from django.shortcuts import redirect
from django.urls import resolve, Resolver404
from django.contrib import messages
from django.conf import settings

class ProfileCompletionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Admins and superusers bypass this check
            if request.user.is_admin or request.user.is_superuser:
                return self.get_response(request)

            # Check if user has completed their profile
            if not request.user.has_completed_profile:
                path = request.path_info
                
                # Always allow Django Admin, Static files, and Media files
                if path.startswith('/admin/') or path.startswith(settings.STATIC_URL) or (settings.MEDIA_URL and path.startswith(settings.MEDIA_URL)):
                    return self.get_response(request)

                try:
                    match = resolve(path)
                    exempt_views = ['complete_profile', 'logout', 'home', 'about', 'services', 'contact', 'login', 'register']
                    if match.url_name in exempt_views:
                        return self.get_response(request)
                except Resolver404:
                    pass

                # Redirect to profile completion page
                if path != '/profile/complete/':
                    messages.warning(request, "Please complete your profile first.")
                    return redirect('complete_profile')

        return self.get_response(request)
