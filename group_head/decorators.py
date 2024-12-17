from django.http import Http404
from functools import wraps
from django.http import HttpResponseForbidden
from functools import wraps

def admin_or_admin_employee_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user is an admin or an admin employee
        if not (getattr(request.user, 'is_admin', False) or getattr(request.user, 'is_admin_employee', False)):
            raise Http404("Page not found")
        return view_func(request, *args, **kwargs)
    return _wrapped_view



def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user has the required admin access
        if not getattr(request.user, 'is_admin', False):
            raise Http404("Page not found")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def employee_user_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the user has the required admin access
        if not getattr(request.user, 'employee_user', False):
            raise Http404("Page not found")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_employee_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not getattr(request.user, 'is_admin_employee', False):
           raise Http404("Page not found")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

