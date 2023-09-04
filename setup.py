from setuptools import setup

readme = ''
with open('README.md') as rf:
    readme = rf.read()

requirements = [
    'SQLAlchemy==2.0.*',
    'typing_extensions==4.7.*'
]

setup(
    name='filterable',
    author="TotvsLabs",
    version='0.0.1',
    author_email='info@totvslabs.com',
    python_requires='>=3.7',
    description="Filterable handler to handle with request filters",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    include_package_data=True,
    keywords=[
        'pagination', 'assistant','handler','helper','filter','request', 'args',
        'paginate', 'filters', 'filtering'
    ],
    packages=[
        'filterable',
        'filterable.exceptions',
        'filterable.helpers',
        'filterable.request',
        'filterable.types'
    ],
    url='https://github.com/totvslabs/filterable'
)