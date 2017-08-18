import pkg_resources
import re


def normalize(project):
    ''' get PEP-503 normalized project name '''
    return re.sub(r"[-_.]+", "-", project).lower()


def get_project_name_from_file(filename):
    # use pkg_resources to find project name for .eggs
    if filename.endswith('.egg'):
        return normalize(pkg_resources.Distribution.from_filename(filename).project_name)
    return normalize(re.search(r'(.*)-\d+\..*', filename).group(1))
