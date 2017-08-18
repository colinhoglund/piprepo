import pkg_resources
import re


def normalize(project):
    ''' get PEP-503 normalized project name '''
    return re.sub(r"[-_.]+", "-", project).lower()


def get_project_name_from_filename(filename):
    # use pkg_resources to find project name for .eggs
    # https://github.com/pypa/setuptools/blob/aa41a7a58d0e1cd0dd6715b2d4057666410114c7/pkg_resources/__init__.py#L2456
    if filename.endswith('.egg'):
        return normalize(pkg_resources.Distribution.from_filename(filename).project_name)
    if filename.endswith('.whl'):
        return normalize(filename.rsplit('-', 4)[0])
    return normalize(re.search(r'(.*)-\d+\..*', filename).group(1))
