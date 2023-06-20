from flask import render_template, Blueprint, request, g, Response
from installies.lib.view import TemplateView
from installies.blueprints.app_manager.groups import AppGroup
from installies.blueprints.app_manager.models import App, Maintainer
from peewee import *

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
    
    return render_template('apps.html', apps=apps)
