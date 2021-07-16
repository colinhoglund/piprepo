import pkg_resources
import re
from pipindex.exceptions import InvalidFileName


def normalize(project):
    ''' get PEP-503 normalized project name '''
    return re.sub(r"[-_.]+", "-", project).lower()


def get_project_name_from_file(filename):
    # PEP-440 compliant version
    # https://www.python.org/dev/peps/pep-0440/#appendix-b-parsing-version-strings-with-regular-expressions
    pep440 = r'([1-9]\d*!)?(0|[1-9]\d*)(\.(0|[1-9]\d*))*((a|b|rc)(0|[1-9]\d*))?(\.post(0|[1-9]\d*))?(\.dev(0|[1-9]\d*))?'

    # use pkg_resources to find project name for .eggs
    if filename.endswith('.egg'):
        return normalize(pkg_resources.Distribution.from_filename(filename).project_name)
    match = re.search(r'(.*)-{}.*'.format(pep440), filename)
    if match:
        return normalize(match.group(1))
    # raise an exception if filename is not a valid python package
    raise InvalidFileName(filename)
