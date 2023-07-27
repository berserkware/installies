import argparse
import requests
import json
import sys
import platform
import distro
import os
from pathlib import Path
import subprocess

__version__ = '0.1.0'

class AppNotFoundError(Exception):
    """Raised when an app is not found."""

class ScriptNotFoundError(Exception):
    """Raised when an script is not found"""

class Installed:
    """An object to get and save the data from ~/.cache/installies/installed.json."""

    def __init__(self, data: dict):
        self.data = data
    
    @classmethod
    def get_or_create(cls):
        """
        Gets the data from the installed.json file.

        If the file doesn't exist, it is created.
        """
        cache_folder = Path(f'~/.config/installies').expanduser()
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)

        installed_apps_file = os.path.join(cache_folder, 'installed.json')
        try:
            f = open(installed_apps_file, 'x')
            f.close()
        except FileExistsError:
            pass
        
        # if file cannot be loaded into json, it is marked as empty
        empty = False
        with open(installed_apps_file, 'r') as f:
            content = f.read()
            try:
                json.loads(content)
            except json.JSONDecodeError:
                empty = True
                
        # if file is empty, write empty json data to it
        if empty:
            with open(installed_apps_file, 'w') as f:
                f.write(json.dumps({'installed_apps': {}}))

        data = {}
        with open(installed_apps_file, 'r') as f:
            data = json.loads(f.read())
            if 'installed_apps' not in data.keys():
                data['installed_apps'] = {}
            
        return cls(data)

    def save(self):
        """Saves the data."""
        installed_apps_file = Path(f'~/.config/installies/installed.json').expanduser()
        with open(installed_apps_file, 'w') as f:
            f.write(json.dumps(self.data))

    
class AppRequest:
    """
    A class to store data the user has given about the app they want to get scripts of.
    """

    def __init__(self, app_name: str):
        split_app_name = args.app_name.split('==')
        
        self.name = split_app_name[0]

        #if the user specifies a version of the app to get
        self.version = (split_app_name[1] if len(split_app_name) == 2 else None)
    

class App:
    """An object for retrieving and storing apps."""

    def __init__(
            self,
            name,
            display_name,
            current_version, 
            creation_date,
            last_modified,
            submitter,
    ):
        self.name = name
        self.display_name = display_name
        self.current_version = current_version
        self.creation_date = creation_date
        self.last_modified = last_modified
        self.submitter = submitter

    @classmethod
    def get(cls, name):
        """Gets an app."""

        params = {
            'name': name,
        }

        r = requests.get(
            url=f'http://localhost:8000/api/apps',
            params=params,
        )

        data = r.json()

        apps = data['apps']

        if len(apps) == 0:
            raise AppNotFoundError()

        app = apps[0]
        
        return cls(
            name=app['name'],
            display_name=app['display_name'],
            current_version=app['current_version'],
            creation_date=app['creation_date'],
            last_modified=app['last_modified'],
            submitter=app['submitter'],
        )
    
    
class Script:
    """An object for retrieving and storing scripts."""

    def __init__(self, app: App, action, content, for_version, last_modified, supported_distros):
        self.app = app
        self.action = action
        self.content = content
        self.for_version = for_version
        self.last_modified = last_modified
        self.supported_distros = supported_distros


    @classmethod
    def get(cls, app, action, distro_id, architechture, for_version=None):
        """Gets a Script or list of Scripts by some parameters."""
        params = {
            'action': action,
            'supports': f'{distro_id}:{architechture}',
        }

        if for_version is not None:
            params['version'] = for_version
        
        r = requests.get(
            url=f'http://localhost:8000/api/apps/{ app.name }/scripts',
            params=params
        )

        if r.status_code == 404:
            raise AppNotFoundError()

        data = r.json()
    
        scripts = data['scripts']

        if len(scripts) == 0:
            raise ScriptNotFoundError()

        script_list = []
        for script in scripts:
            script_list.append(
                cls(
                    app=app,
                    **script
                )
            )

        if len(script_list) == 1:
            return script_list[0]

        return script_list


    def create_file(self):
        """Create a bash file for the script. Returns the path to the file."""
        path_to_app = Path(f'~/.cache/installies/{self.app.name}').expanduser()
        if not os.path.exists(path_to_app):
            os.makedirs(path_to_app)

        path = f'{path_to_app}/{self.action}.sh'
        with open(path, 'w') as f:
            f.write(self.content)

        os.system(f'chmod +x {path}')
        return path


class ActionHandler:
    """
    Handles actions like install, remove, compile or update.

    :param app_request: The AppRequest.
    """

    def __init__(self, app_request):
        self.app_request = app_request
        self.installed = Installed.get_or_create()

    def handle(self, action: str, args):
        """Handles an action."""

        try:
            function = getattr(self, f'handle_{action}')
        except AttributeError:
            print('Unsupported action.')
            sys.exit()

        app = self.get_app()

        script = self.get_script(app, action='install')

        function(app, script, args)

        self.installed.save()
        

    def handle_install(self, app, script, args):
        """Handles installing apps."""

        if app.name in self.installed.data['installed_apps'].keys():
            answer = input(f':: {app.name} is already installed, run script anyway?  [Y,n] ')
            if answer != 'Y':
                sys.exit()

        self.run_script('install', script)

        version = script.app.current_version
        if self.app_request.version is not None:
            version = self.app_request.version
        
        self.installed.data['installed_apps'][self.app_request.name] = version 

    def handle_remove(self, app, script, args):
        """Handles removing apps."""
        
        if app.name not in self.installed.data['installed_apps'].keys():
            answer = input(f':: {app.name} isn\'t installed, run script anyway?  [Y,n] ')
            if answer != 'Y':
                sys.exit()
        
        self.run_script('remove', script)

        if app_request.name in installed['installed_apps'].keys():
            del self.installed.data['installed_apps'][app_request.name]

    def handle_compile(self, app, script, args):
        """Handles compiling apps."""

        if app.name in self.installed.data['installed_apps'].keys():
            answer = input(f':: {app.name} is already installed, run script anyway?  [Y,n] ')
            if answer != 'Y':
                sys.exit()

        self.run_script('compile', script)

        version = script.app.current_version
        if self.app_request.version is not None:
            version = self.app_request.version
        
        self.installed.data['installed_apps'][self.app_request.name] = version

    def handle_update(self, app, script,args):
        """Handles updating apps."""

        if app.name not in self.installed.data['installed_apps'].keys():
            answer = input(f':: {app.name} isn\'t installed, run script anyway?  [Y,n] ')
            if answer != 'Y':
                sys.exit()

        self.run_script('update', script)

        version = script.app.current_version
        if self.app_request.version is not None:
            version = self.app_request.version
        
        self.installed.data['installed_apps'][self.app_request.name] = version

    def run_script(self, action: str, script: Script):
        """
        Runs a script.

        :param action: The action the script is doing.
        :param script: The script to run.
        """
        version = script.app.current_version
        if self.app_request.version is not None:
            version = self.app_request.version
        script.content = script.content.replace('<version>', version)
        
        script_file_path = script.create_file()
        
        # warns user if cli is running in sudo mode
        if os.getuid() == 0:
            answer = input(
                '\033[38;5;214mWarning: You are running the script in sudo mode, do you want to continue? [Y,n] '
            )
            if answer != 'Y':
                sys.exit()

        if args.output_script:
            print(':: Script Content Start')
            print(script.content)
            print(':: Script Content End')
            print('')
            
        answer = input(':: Proceed? [Y,n] ')
        if answer != 'Y':
            sys.exit()
            
        print(f'-- Executing {action} script. --')
        subprocess.run([script_file_path], shell=True)
        
    def get_app(self):
        """Gets an App object."""
        try:
            app = App.get(name=self.app_request.name)
        except AppNotFoundError:
            print(f"\033[31mError: No matching app found for {self.app_request.name}")
            sys.exit()

        return app

    def get_script(self, app, **args):
        """
        Gets a Script object.

        :param app: The app to get the script of.
        :param args: The extra args for Script.get.
        """

        distro_id = distro.id()
        architechture = platform.machine()
        if architechture == 'x86_64':
            architechture = 'amd64'

        try:
            script = Script.get(
                app=app,
                distro_id=distro_id,
                architechture=architechture,
                for_version=self.app_request.version,
                **args,
            )

        except ScriptNotFoundError:
            print(f"\033[31mError: No matching script found for {distro_id}: {architechture}")
            sys.exit()

        return script
    

if __name__ == '__main__':
    main_parser = argparse.ArgumentParser(
        prog='installies',
    )
    main_parser.add_argument('-v', '--version', action='store_true', help="show version")
    subparsers = main_parser.add_subparsers(
        title="Commands"
    )

    action_parser = argparse.ArgumentParser()
    action_parser.add_argument(
        '-o',
        '--output-script',
        action='store_true',
        help="shows the script before exectuting"
    )
    action_parser.add_argument('app_name')
    
    install_parser = subparsers.add_parser(
        "install",
        help="Installs apps",
        parents=[action_parser],
        add_help=False
    )
    install_parser.set_defaults(action='install')

    remove_parser = subparsers.add_parser(
        "remove",
        help="Removes apps",
        parents=[action_parser],
        add_help=False
    )
    remove_parser.set_defaults(action='remove')

    update_parser = subparsers.add_parser(
        "update",
        help="Updates apps",
        parents=[action_parser],
        add_help=False
    )
    update_parser.set_defaults(action='update')

    compile_parser = subparsers.add_parser(
        "compile",
        help="Compiles apps",
        parents=[action_parser],
        add_help=False
    )
    compile_parser.set_defaults(action='compile')
    
    args = main_parser.parse_args()

    if args.version:
        print(f'Installies CLI v{__version__}')

    try:
        if hasattr(args, 'action'):
            app_request = AppRequest(args.app_name)
            handler = ActionHandler(app_request)
            handler.handle(args.action, args)
    except KeyboardInterrupt:
        print('\nKeyboardInterrupt, Aborting.')
        sys.exit()

    print('Nothing To Do.')
