from flask import Blueprint, render_template, request, flash, redirect, url_for
from installies.apps.auth.decorators import authenticated_required
from installies.apps.admin.decorators import admin_required
from installies.apps.app_manager.models import Distro
from installies.lib.validate import ValidationError
from installies.apps.admin.validate import DistroSlugValidator, DistroNameValidatior

admin = Blueprint('admin', __name__)

@admin.route('/admin')
@authenticated_required()
@admin_required()
def admin_stats():
    return render_template('admin/statistics.html')

@admin.route('/admin/add-distro', methods=['get', 'post'])
@authenticated_required()
@admin_required()
def add_distro():
    supported_distros = Distro.get_all_distro_slugs()

    if request.method == 'POST':
        name = request.form.get('distro-name')
        slug = request.form.get('distro-slug')
        based_on = request.form.get('distro-based-on')

        try:
            DistroNameValidatior.validate(name)
            DistroSlugValidator.validate(slug)
        except ValidationError as e:
            flash(str(e), 'error')
            return redirect(url_for('admin.add_distro'))

        # checks that there is a distro that exists with the based on slug
        based_on_distro = Distro.select().where(Distro.slug == based_on)
        if based_on_distro.exists() is False:
            flash(f'Could not find distro to be based with the slug "{based_on}"', 'error')
            return redirect(url_for('admin.add_distro'))

        based_on_distro = based_on_distro.get()

        distro = Distro.create(name=name, slug=slug, based_on=based_on_distro)

        flash('Distro successfully created.', 'success')
        return redirect(url_for('admin.admin_stats'))
        
    return render_template(
        'admin/add_distro.html',
        supported_distros=supported_distros
    )
