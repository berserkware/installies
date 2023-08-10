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

        
def confirm(prompt: str):
    """
    Asks the user a yes or no question.

    If the user replies with anything other that "Y", False is returned, else True. The string
    " [Y/n]" is appended to the ending of the prompt.

    :param prompt: The question to ask the user.
    """

    answer = input(f'{prompt} [Y/n] ')
    if answer != 'Y':
        return False

    return True

def script_selecter(scripts: list):
    """
    Allows the user to select a script in the list. Returns the script the user chose.

    If there is only one script in the list, it returns that.

    :param scripts: The script to get the user to select from.
    """

    if len(scripts) == 1:
        return scripts[0]
    
    print(f'==> Please select a script to use.')

    # gets the length of the longest script method
    max_method_char_length = len(scripts[0].method)
    for script in scripts:
        if len(script.method) > max_method_char_length:
            max_method_char_length = len(script.method)
    
    for i, script in enumerate(scripts):
        # gets the amount of spacing needed to make the length of the methods equal
        method_spacing = "".join([" " for i in range(0, max_method_char_length-len(script.method))])
        
        print(f'{i} {script.method}{method_spacing} - Supported Actions: {", ".join(script.actions)}')

    while True:
        try:
            script_index = int(input(f'==> Please select a number between 0 and {len(scripts)-1}: '))
        except ValueError:
            print('Please enter a number.')
            continue

        # checks the script index is lest than the script length, and that the index is more or equal to zero.
        if script_index < len(scripts) and script_index >= 0:
            break

        print(f'Please enter a number between 0 and {len(scripts)-1}. ')

    return scripts[script_index]


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

    def check_installed(self, app_name):
        """Checks if the given app is installed."""

        if app_name in self.data['installed_apps']:
            return True

        return False
            
class AppRequest:
    """
    A class to store data the user has given about the app they want to get scripts of.
    """

    def __init__(self, app_name: str):
        split_app_name = args.app_name.split('==')
        
        self.name = split_app_name[0]

        #if the user specifies a version of the app to get
        self.version = (split_app_name[1] if len(split_app_name) == 2 else None)
            
    
class Script:
    """An object for retrieving and storing scripts."""

    def __init__(self, id, actions, method, content, version):
        self.id = id
        self.actions = actions
        self.method = method
        self.content = content
        self.version = version

    @classmethod
    def get_app(cls, app_request):
        """
        Gets the data of an app from a request.

        :param app_request: The data of the app to get.
        """
        apps = requests.get(
            url=f'http://localhost:8000/api/apps',
            params={'name': app_request.name},
        ).json()['apps']

        if len(apps) == 0:
             print(f"\033[31mError: No matching app found for {app_request.name}")
             sys.exit()

        app = apps[0]
        
        return app
        
    @classmethod
    def get(cls, app_request, action, distro_id, architechture, script_id=None):
        """Gets a script."""
        app = cls.get_app(app_request)
        
        params = {
            'actions': action,
            'supports': f'{distro_id}:{architechture}',
        }

        if app_request.version is not None:
            params['version'] = app_request.version

        if script_id is not None:
            params['id'] = script_id
        
        r = requests.get(
            url=f'http://localhost:8000/api/apps/{ app_request.name }/scripts',
            params=params
        )

        data = r.json()
    
        scripts = data['scripts']

        version = None
        if app_request.version is not None:
            version = app_request.version
        elif app['current_version'] is not None:
            version = app['current_version']

        script_list = []
        for script in scripts:
            script_list.append(Script(
                id=script['id'],
                actions=script['actions'],
                method=script['method'],
                content=script['content'],
                version=(version if version is not None else script['for_version']),
            ))

        if len(script_list) == 0:
            print(f"\033[31mError: No matching script found.\033[0m")
            sys.exit()

        script = script_selecter(script_list)

        return script

    @classmethod
    def check_content_cached(cls, app_name):
        """Returns True if there is a no empty script present in the cache for the app, else False."""
        path_to_cache = Path(f'~/.cache/installies').expanduser()
        if not os.path.exists(path_to_cache):
            os.makedirs(path_to_cache)

        # checks that file exists
        path_to_script = Path(f'{path_to_cache}/{app_name}.sh')
        if path_to_script.is_file() is False:
            return False

        # checks if script file is empty
        with open(path_to_script, 'r') as f:
            content = f.read()
            if content.strip() == '':
                return False

        return True
    
    @classmethod
    def get_cached_content(cls, app_name):
        """Gets the cached script content for the given app."""
        path_to_cache = Path(f'~/.cache/installies').expanduser()
        if not os.path.exists(path_to_cache):
            os.makedirs(path_to_cache)

        path = f'{path_to_cache}/{app_name}.sh'
        with open(path, 'r') as f:
            return f.read()

    def create_file(self, app_name):
        """
        Create a bash file for the script. Returns the path to the file.

        :param app_name: The name of the app the script is for.
        """
        path_to_cache = Path(f'~/.cache/installies').expanduser()
        if not os.path.exists(path_to_cache):
            os.makedirs(path_to_cache)

        path = f'{path_to_cache}/{app_name}.sh'
        with open(path, 'w') as f:
            f.write(self.content)

        os.system(f'chmod +x {path}')
        return path

    def run(self, app_name, action, args):
        """Runs this script."""

        if args.output_script:
            print(':: Script Content Start')
            print(self.content)
            print(':: Script Content End\n')
        
        # warns user if cli is running in sudo mode
        if os.getuid() == 0:
            if confirm('\033[38;5;214mWarning: You are running the script in sudo mode, do you want to continue?\033[0m') is False:
                sys.exit()

        if confirm(f':: Continue with {action}?') is False:
            sys.exit()

        script_file_path = self.create_file(app_name)
        
        print(f'-- Begin executing script. --')
        subprocess.run(f'{script_file_path} {action}', shell=True)
        print(f'--  End executing script.  --')


class ActionHandler:
    """
    A class to handle actions like install, remove, update, compile, or run.

    :param app_request: The AppRequest to get.
    :param install_actions: Actions that install apps.
    :param modify_actions: Actions that modify the current installation.
    :param remove_actions: Actions that remove the installation.
    """

    def __init__(
            self,
            app_request,
            install_actions=[],
            modify_actions=[],
            remove_actions=[],
    ):
        self.app_request = app_request
        self.install_actions = install_actions
        self.modify_actions = modify_actions
        self.remove_actions = remove_actions
        
        self.distro_id = distro.id()
        
        architechture = platform.machine()
        if architechture == 'x86_64':
            architechture = 'amd64'
        self.architechture = architechture

        self.installed = Installed.get_or_create()

    def get_script(self, action):
        """Gets a script for an action."""

        # if the action modifies the current installation, ask user if they want to use the
        # same script they used to install. If the script no longer exists, alert the user and
        # quit.
        if action in self.modify_actions and self.installed.check_installed(self.app_request.name):
            if Script.check_content_cached(self.app_request.name) and confirm('Do you want to use the same script used to install the app?') is True:
                print('==> Cached script found, do you want to use it?:')
                print('1 Use the cached script.')
                print('2 Get a new version of the script.')
                while True:
                    try:
                        option = int(input('==> Choose Option [1/2]: '))

                        if option < 1 or option > 2:
                            print('Please enter 1 or 2.')
                            continue

                        break
                    except ValueError:
                        print('Please enter a number.')
                        continue
                    
                script_data = self.installed.data['installed_apps'][self.app_request.name]['script']
                if option == 1:
                    return Script(
                        id=script_data['id'],
                        actions=script_data['actions'],
                        method=script_data['method'],
                        content=Script.get_cached_content(self.app_request.name),
                        version=self.installed.data['installed_apps'][self.app_request.name]['version']
                    )
                elif option == 2:
                    script_id = self.installed.data['installed_apps'][self.app_request.name]['script']['id']
                    scripts = Script.get(
                        self.app_request,
                        args.action,
                        distro_id=self.distro_id,
                        architechture=self.architechture,
                        script_id=script_id
                    )
                    
                    if len(scripts) == 0:
                        print(f'\033[31mError: Script no longer exists, or doesn\'t support the given action.\033[0m')
                        sys.exit()
                            
                    return scripts[0]
            else:
                return Script.get(
                     self.app_request,
                     args.action,
                     distro_id=self.distro_id,
                     architechture=self.architechture,
                 )
        else:
            return Script.get(
                self.app_request,
                args.action,
                distro_id=self.distro_id,
                architechture=self.architechture,
            )
        
    def handle(self, action, args):
        """
        Handles an action.

        :param action: The action to match to a method.
        :param args: The args to pass to the method.
        """

        if action in self.modify_actions and self.installed.check_installed(self.app_request.name) is False:
            if confirm(':: App is not installed, are you sure you want to proceed?') is False:
                sys.exit()

        # if action is an installing action and app is already installed, confirm user wants to
        # run the script.
        if action in self.install_actions and self.app_request.name in self.installed.data['installed_apps'].keys():
            if confirm(':: App already installed, are you sure you want to proceed?') is False:
                sys.exit()

        script = self.get_script(action)

        script.run(self.app_request.name, action, args)

        # if the action is an install action, add the app to the installed_apps file.
        if action in self.install_actions:
            self.installed.data['installed_apps'][self.app_request.name] = {
                'version': script.version,
                'script': {
                    'id': script.id,
                    'actions': script.actions,
                    'method': script.method,
                }
            }
            self.installed.save()
        # else if the action is a remove action, remove it from the file.
        elif action in self.remove_actions:
            if self.app_request.name in self.installed.data['installed_apps']:
                del self.installed.data['installed_apps'][self.app_request.name]
                self.installed.save()


def create_parser():
    """Creates the parser."""
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
        help="shows the script before executing"
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

    run_parser = subparsers.add_parser(
        "run",
        help="Runs a script on a app.",
        parents=[action_parser],
        add_help=False
    )
    run_parser.set_defaults(action='run')

    return main_parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    if args.version:
        print(f'Installies CLI v{__version__}')

    if not hasattr(args, 'action'):
        sys.exit()

    action_handler = ActionHandler(
        AppRequest(args.app_name),
        install_actions=[
            'install',
            'compile,'
        ],
        modify_actions=[
            'update',
            'remove',
        ],
        remove_actions=[
            'remove'
        ]
    )

    try:
        action_handler.handle(args.action, args)
    except KeyboardInterrupt:
        print('')
        sys.exit()
