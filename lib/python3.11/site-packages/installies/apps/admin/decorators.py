from functools import wraps
from flask import redirect, flash, g

def admin_required():
    """A decorator that only allowed users who are admin to access the page."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if g.user.admin is not True:
                flash('You must be admin to access this page.', 'error')
                return redirect('/')

            return func(*args, **kwargs)

        return wrapper
    return decorator
        
