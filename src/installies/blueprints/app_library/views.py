from flask import render_template, Blueprint, request, g, Response
from installies.lib.view import TemplateView
from installies.groups.app import AppGroup
from installies.groups.modifiers import Paginate
from installies.models.app import App
from installies.models.maintainer import Maintainer
from installies.models.report import AppReport
from peewee import *

import math

app_library = Blueprint('app_library', __name__)

class IndexView(TemplateView):
    template_path = 'index.html'

    def get_context_data(self, **kwargs):
        if g.is_authed:
            user_maintained_apps = (
                AppGroup
                .get()
                .where(Maintainer.user == g.user)
                .paginate(1, 10)
                .distinct()
            )
            kwargs['user_maintained_apps'] = user_maintained_apps

        return kwargs

app_library.add_url_rule('/', 'index', view_func=IndexView.as_view())
    
@app_library.route('/apps')
def apps():
    apps = AppGroup.get(**request.args).where(
        ((Maintainer.user == g.user) & (App.visibility != 'public')) | (App.visibility == 'public')
    )

    paginator = Paginate(
        default_per_page = 10,
        max_per_page = 50,
    )

    paginated_apps = paginator.modify(apps, **request.args)
    
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
