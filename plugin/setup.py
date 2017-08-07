from setuptools import setup

import octoprint_setuptools

plugin_identifier = 'osminog'
plugin_package = 'octoprint_osminog'
plugin_name = 'Osminog'
plugin_version = '0.1.0'
plugin_description = 'Control your printer with Osminog.'
plugin_author = 'Adam Coddington'
plugin_author_email = 'me@adamcoddington.net'
plugin_url = 'https://github.com/coddingtonbear/osminog'
plugin_license = 'MIT'
plugin_requires = []

plugin_additional_data = []
plugin_additional_packages = []
plugin_ignored_packages = []


setup_parameters = octoprint_setuptools.create_plugin_setup_parameters(
    identifier=plugin_identifier,
    package=plugin_package,
    name=plugin_name,
    version=plugin_version,
    description=plugin_description,
    author=plugin_author,
    mail=plugin_author_email,
    url=plugin_url,
    license=plugin_license,
    requires=plugin_requires,
    additional_packages=plugin_additional_packages,
    ignored_packages=plugin_ignored_packages,
    additional_data=plugin_additional_data
)

setup(**setup_parameters)
