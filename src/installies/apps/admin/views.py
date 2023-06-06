from flask import Blueprint, render_template, request, flash, redirect, url_for, g
from installies.apps.auth.decorators import authenticated_required
from installies.apps.admin.decorators import admin_required
from installies.apps.app_manager.models import Distro
from installies.lib.validate import ValidationError
from installies.apps.admin.validate import DistroSlugValidator, DistroNameValidatior
from installies.lib.view import FormView, AuthenticationRequiredMixin, TemplateView
from installies.apps.admin.form import CreateDistroForm

admin = Blueprint('admin', __name__)

class AdminRequiredMixin:
    """A mixin for only allowing access to admins."""

    def on_request(self, **kwargs):
        if g.user.admin is False:
            flash('You must be admin to access this page.', 'error')
            return redirect('/')

        return super().on_request(**kwargs)


class AdminOptions(AuthenticationRequiredMixin, AdminRequiredMixin, TemplateView):
    """A view for displaying admin options."""

    template_path = 'admin/options.html'

    
class AddDistroView(AuthenticationRequiredMixin, AdminRequiredMixin, FormView):
    """A view for adding distros."""

    template_path = 'admin/add_distro.html'
    form_class = CreateDistroForm

    def form_valid(self, form, **kwargs):
        based_on = form.data['distro-based-on']
        based_on_distro = None
        if based_on is not None and based_on != '':
            
            # checks that there is a distro that exists with the based on slug
            based_on_distro = Distro.select().where(Distro.slug == based_on)
            if based_on_distro.exists() is False:
                flash(f'Could not find distro to be based with the slug "{based_on}"', 'error')
                return redirect(url_for('admin.add_distro'))

            based_on_distro = based_on_distro.get()

        distro = form.save(based_on=based_on_distro)

        flash('Distro successfully created.', 'success')
        return redirect(url_for('admin.admin_options'))


admin.add_url_rule('/admin', 'admin_options', AdminOptions.as_view())    
admin.add_url_rule('/admin/add-distro', 'add_distro', AddDistroView.as_view(), methods=['get', 'post'])
