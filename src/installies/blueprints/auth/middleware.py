from installies.models.user import User
from peewee import DoesNotExist
from waffleweb.response import TemplateResponse

import bleach

class IsAuthenticated:
    """
    A middleware that checks the auth cookies, and if one exists,
    It matches it in the database, and adds a IsAuthed attr to the
    request. It also adds the user data to the response, if it is
    a TemplateResponse.
    """

    def before(self, request):
        # Sets the userdata to none
        self.is_authed = False
        self.username = None

        token = request.COOKIES.get('user-token')

        # Checks that cookie exists
        if token is None:
            request.is_authed = False
            return request
        
        try:
            user = User.get(User.token == token)
        except DoesNotExist:
            request.is_authed = False
            return request

        # Sets the userdata to the database data of the user.
        self.user = user
        self.is_authed = True

        request.is_authed = True
        request.user = user

        return request

    def after(self, response):

        #Checks that the response is a template one
        if type(response) != TemplateResponse:
            return response

        # Gets the variables of the TemplateResponse
        new_context = response.context.copy()
        new_context['is_authed'] = self.is_authed

        # adds the new user-specific variables
        if self.is_authed:
            username = bleach.clean(self.user.username)
            new_context['authed_username'] = username

        new_context['is_authed'] = self.is_authed

        # Sets the new variables
        response.context = new_context

        return response
