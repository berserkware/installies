from flask import request, abort, render_template, g, redirect, flash

class View:
    """
    A class for creating views.

    Use the ``as_view`` method to add the view to the flask app. Methods named after request
    methods in the ``method_names `` attribute will be called if the request is of that method.
    """

    method_names = [
        'head',
        'get',
        'post',
    ]
    
    @classmethod
    def as_view(cls):
        """An entry point that allows flask apps to give requests to this view."""

        def view(**kwargs):
            self = cls()
            return self.on_request(**kwargs)
        return view

    def on_request(self, **kwargs):
        """Runs on a request."""

        if request.method.lower() in self.method_names:
            handler = getattr(
                self, request.method.lower()
            )
            return handler(**kwargs)
        else:
            abort(405)


class TemplateMixin:
    """
    A mixin for returning templates to the user.

    The template path is put in the ``template_path`` attribute.
    """

    template_path = ''

    def get_context_data(self, **kwargs):
        """Gets the context data for the template. Returns the passed in kwargs."""
        return kwargs
    
class TemplateView(TemplateMixin, View):
    """A view for returning templates to the user."""

    def get(self, **kwargs):
        context = self.get_context_data(**kwargs)
        return render_template(self.template_path, **context)

class DetailMixin:
    """A mixin for getting details about a model."""

    model = None
    model_name = None

    def get_object(self, **kwargs):
        """Gets the model to put in the template."""
        return self.model.get()

    def get_name(self):
        """Gets the name of the model."""
        if self.model_name is None:
            return self.model.__name__.lower()
        return self.model_name
    
class DetailView(DetailMixin, TemplateMixin, View):
    """A view for giving data about a model to the user."""
    
    def get(self, **kwargs):
        model = self.get_object(**kwargs)
        model_name = (self.model_name if self.model_name is not None else model.__name__.lower())
        kwargs[model_name] = model
        
        context = self.get_context_data(**kwargs)
        return render_template(self.template_path, **context)
        
class ListMixin:
    """A mixin for getting lists of objects."""

    group = None
    group_name = None

    def get_group(self, **kwargs):
        """
        Gets the group of objects.
        """
        return self.group.get(**requests.args)

class ListView(ListMixin, TemplateMixin, View):
    """A view for returning groups of objects to the user."""

    def get(self, **kwargs):
        group = self.get_group(**kwargs)
        kwargs[self.group_name] = group

        context = self.get_context_data(**kwargs)
        return render_template(self.template_path, **context)

class FormMixin:
    """
    A mixin for getting form data.
    """

    form_class = None

    def get_success_url(self):
        """Gets the url to redirect to if the form is successful."""
        return '/'
        
    def form_valid(self, form, **kwargs):
        """Runs when the form is valid."""
        return redirect(self.get_success_url(), 303)

    def form_invalid(self, form, **kwargs):
        """Runs when the form is invalid."""
        flash(form.error, 'error')
        return self.get(**kwargs)


class FormView(FormMixin, TemplateMixin, View):
    """A class for viewing forms."""

    def get(self, **kwargs):
        context = self.get_context_data(**kwargs)
        return render_template(self.template_path, **context)

    def post(self, **kwargs):
        form = self.form_class(request.form)

        if form.is_valid():
            return self.form_valid(form, **kwargs)
        else:
            return self.form_invalid(form, **kwargs)


class AuthenticationRequiredMixin:
    """A mixin for only allowing authenticated user."""

    def on_request(self, **kwargs):
        if g.is_authed == False:
            return redirect(f'/login?referer={request.path}')

        return super().on_request(**kwargs)
