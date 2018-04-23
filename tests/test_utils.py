from piprepo import models, utils
from .conftest import PACKAGES


def test_project_names():
    expected = {
        'affinitic-recipe-fakezope2eggs',
        'ansible',
        'avocado-framework-plugin-varianter-yaml-to-mux',
        'django',
        'foursquare',
        'python-http-client'
    }

    assert {utils.get_project_name_from_file(p) for p in PACKAGES} == expected


def test_skip_invalid_package(tempindex):
    index = models.LocalIndex(tempindex['source'], tempindex['destination'])
    index._build_packages(['invalidpackage.txt'])
    assert index.packages == {}
