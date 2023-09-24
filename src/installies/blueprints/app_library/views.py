from flask import render_template, Blueprint, request, g, Response
from installies.lib.view import TemplateView
from installies.groups.app import AppGroup
from installies.groups.script import ScriptGroup
from installies.groups.modifiers import Paginate
from installies.models.app import App
from installies.models.maintainer import Maintainer
from peewee import *
from installies.lib.email import send_email

import math

app_library = Blueprint('app_library', __name__)

class IndexView(TemplateView):
    template_path = 'index.html'

    def get_context_data(self, **kwargs):
        if g.is_authed:
            user_maintained_apps = (
                AppGroup
                .get({'search-in': 'maintainers', 'k': g.user.username})
                .paginate(1, 10)
            )
            user_maintained_scripts = (
                 ScriptGroup
                .get({'search-in': 'maintainers', 'k': g.user.username})
                .paginate(1, 10)
            )
            kwargs['user_maintained_apps'] = user_maintained_apps
            kwargs['user_maintained_scripts'] = user_maintained_scripts

        recently_updated_apps = (
            AppGroup
            .get({
                'sort-by': 'last_modified',
                'order-by': 'desc',
            })
            .paginate(1, 10)
        )
        kwargs['recently_updated_apps'] = recently_updated_apps

        newest_apps = (
            AppGroup
            .get({
                'sort-by': 'creation_date',
                'order-by': 'desc',
            })
            .paginate(1, 10)
        )
        kwargs['newest_apps'] = newest_apps
        
        return kwargs

app_library.add_url_rule('/', 'index', view_func=IndexView.as_view())
    
@app_library.route('/apps')
def apps():
    apps = AppGroup.get(request.args)

    paginator = Paginate(
        default_per_page = 10,
        max_per_page = 50,
    )

    paginated_apps = paginator.modify(apps, request.args)
    
    total_app_count = apps.count()
    try:
        per_page = int(request.args.get('per-page', 10))
    except ValueError:
        per_page = 10

    page_count = math.ceil(total_app_count / per_page)

    return render_template(
        'apps.html',
        apps=paginated_apps,
        total_app_count=total_app_count,
        page_count=page_count,
    )


@app_library.route('/scripts')
def scripts():
    scripts = ScriptGroup.get(request.args)

    paginator = Paginate(
        default_per_page = 10,
        max_per_page = 50,
    )

    paginated_scripts = paginator.modify(scripts, request.args)

    total_script_count = scripts.count()
    try:
        per_page = int(request.args.get('per-page', 10))
    except ValueError:
        per_page = 10

    page_count = math.ceil(total_script_count / per_page)

    return render_template(
        'scripts.html',
        page_count=page_count,
        scripts=paginated_scripts,
    )


@app_library.route('/support')
def support():
    return render_template('support.html')
