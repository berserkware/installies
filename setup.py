from setuptools import setup

setup(
    name='installies',
    version='0.1.0',
    packages=[
        'installies', 
        'installies.database',
        'installies.static',
        'installies.templates',
        'installies.lib',
        'installies.models',
        'installies.groups',
        'installies.blueprints.api',
        'installies.blueprints.app_library',
        'installies.blueprints.app_manager',
        'installies.blueprints.auth',
        'installies.blueprints.admin'
        ],
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'peewee',
        'flask',
        'bleach',
        'bcrypt',
        'pymysql',
        'python-dotenv',
    ],
)
