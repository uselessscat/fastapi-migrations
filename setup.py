'''
Fastapi migrations
--------------
# TODO: description here
'''
from setuptools import setup

version = open('__version__').read()
long_description = open('README.md', 'r').read()
requirements = open('requirements.txt', 'r').read().splitlines()

setup(
    name='fastapi-migrations',
    version=version,
    url='https://github.com/uselessscat/fastapi-migrations',
    project_urls={
        'Code': 'https://github.com/uselessscat/fastapi-migrations',
        'Issue tracker': 'https://github.com/uselessscat/fastapi-migrations/issues',
    },
    license='MIT',
    author='Ariel Carvajal',
    author_email='arie.cbpro@gmail.com',
    description=('#TODO'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['fastapi_migrations'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=requirements,
    tests_require=[
    ],
    entry_points={
    },
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
