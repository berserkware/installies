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
        'installies.apps.api',
        'installies.apps.app_library',
        'installies.apps.app_manager',
        'installies.apps.auth',
        'installies.apps.admin'
        ],
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'bleach',
        'bcrypt',
        'mysql-connector-python'
    ],
)
