from flask import g, redirect, request
from functools import wraps

def authenticated_required(redirect_to: str=None):
    """
    A decorator that only allows authenticated users to access the page.

    :param redirect_to: The url to redirect to if user is not authenticated. Default
    is login with the referer as the requested page's path.
    """
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if g.is_authed == False:
                if redirect_to is None:
                    return redirect(f'/login?referer={request.path}')
                return redirect(redirect_to)
            
            return func(*args, **kwargs)

        return wrapper
    return decorator
                

def unauthenticated_required(redirect_to: str='/'):
    """
    A decorator that only allowed unauthenticated users to access the page.

    :param redirect_to: The url to redirect to if the user is authenticated.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if g.is_authed == True:
                return redirect(redirect_to)

            return func(*args, **kwargs)

        return wrapper
    return decorator
