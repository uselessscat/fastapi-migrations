# type: ignore

'''
Fastapi migrations
--------------
A small integration between Fastapi and Alembic.
'''
from setuptools import setup
from toml import load

pyproject = load('pyproject.toml')

long_description = open('README.md', 'r').read()

setup_info = pyproject.get('tool').get('poetry')
version = setup_info.get('version')
requirements = setup_info.get('dependencies').keys()
dev_requirements = setup_info.get('dev-dependencies').keys()


setup(
    name='fastapi-migrations',
    version=version,
    url='https://github.com/patiprecios/fastapi-migrations',
    project_urls={
        'Code': 'https://github.com/patiprecios/fastapi-migrations',
        'Issues': 'https://github.com/patiprecios/fastapi-migrations/issues',
    },
    license='MIT',
    author='Ariel Carvajal',
    author_email='arie.cbpro@gmail.com',
    description=('A small integration between Fastapi and Alembic.'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['fastapi_migrations'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=requirements,
    tests_require=dev_requirements,
    test_suite='tests',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
