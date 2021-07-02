import os
import pytest
import shutil
import tempfile

PACKAGES = [
    'Django-1.11.2-py2.py3-none-any.whl',
    'ansible-2.0.0.0.tar.gz',
    'ansible-2.3.1.0.tar.gz',
    'python_http_client-2.2.1-py2.py3-none-any.whl',
    'avocado-framework-plugin-varianter-yaml-to-mux-53.0.tar.gz',
    'affinitic.recipe.fakezope2eggs-0.3-py2.4.egg',
    'foursquare-1!2016.9.12.tar.gz'
]
YANKED_PACKAGES = {
    'foursquare-1!2016.9.12.tar.gz.yank': 'yanked because of reasons',
}


@pytest.yield_fixture(scope="function")
def tempindex():
    temp = tempfile.mkdtemp()
    index = {
        'packages': PACKAGES,
        'yanked_packages': YANKED_PACKAGES,
        'source': os.path.join(temp, 'source'),
        'destination': os.path.join(temp, 'destination'),
    }
    os.mkdir(index['source'])
    os.mkdir(index['destination'])
    for package in index['packages']:
        with open(os.path.join(index['source'], package), 'w') as f:
            f.write(package)
    for package, yank_reason in index['yanked_packages'].items():
        with open(os.path.join(index['source'], package), 'w') as f:
            f.write(yank_reason)
    yield index
    shutil.rmtree(temp)
