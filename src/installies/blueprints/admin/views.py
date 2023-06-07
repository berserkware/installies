from flask import Blueprint, render_template, request, flash, redirect, url_for, g
from installies.blueprints.auth.decorators import authenticated_required
from installies.blueprints.admin.decorators import admin_required
from installies.blueprints.app_manager.models import Distro
from installies.lib.validate import ValidationError
from installies.blueprints.admin.validate import DistroSlugValidator, DistroNameValidatior
from installies.lib.view import FormView, AuthenticationRequiredMixin, TemplateView
from installies.blueprints.admin.form import CreateDistroForm, CreateArchitechtureForm

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


class AddArchitechtureView(AuthenticationRequiredMixin, AdminRequiredMixin, FormView):
    """A view for adding architechture."""

    template_path = 'admin/add_architechture.html'
    form_class = CreateArchitechtureForm

    def form_valid(self, form, **kwarg):
        form.save()         

        flash('Architechture successfully created.', 'success')
        return redirect(url_for('admin.admin_options'))
        
    
admin.add_url_rule('/admin', 'admin_options', AdminOptions.as_view())    
admin.add_url_rule('/admin/add-distro', 'add_distro', AddDistroView.as_view(), methods=['get', 'post'])
admin.add_url_rule('/admin/add-architechture', 'add_architechture', AddArchitechtureView.as_view(), methods=['get', 'post'])
