from flask import request, abort, render_template

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


class TemplateView(View):
    """
    A view for returning templates to the user.

    The template path is put in the ``template_path`` attribute. The ``get_context_data'' method
    is used for getting context for the template.
    """

    template_path = ''

    def get_context_data(self, **kwargs):
        return {}
    
    def get(self, **kwargs):
        context = self.get_context_data(**kwargs)
        return render_template(self.template_path, **context)
