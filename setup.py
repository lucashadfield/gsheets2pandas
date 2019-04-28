from setuptools import setup, find_packages

setup(
    name='gsheets2pandas',
    version='0.3.0',
    author='Lucas Hadfield',
    packages=find_packages(),
    install_requires=[
        'pandas', 'oauth2client', 'google-api-python-client', 'httplib2', 'pytest'
    ]
)
