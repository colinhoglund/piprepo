import os
import re


class Index(object):
    html_header = '<!DOCTYPE html><html><body>\n'
    html_footer = '</body></html>\n'

    def __init__(self, directory):
        self.directory = directory
        self.index_root = directory.rstrip('/') + '/simple'
        self.packages = self._build_packages()

    def _build_packages(self):
        packages = {}
        files = [f for f in os.listdir(self.directory) if os.path.isfile(self.directory + '/' + f)]
        for p in files:
            name = os.path.basename(p).split('-')[0]
            # normalize name as per https://www.python.org/dev/peps/pep-0503/
            name = re.sub(r"[-_.]+", "-", name).lower()
            if name in packages:
                packages[name].append(p)
            else:
                packages[name] = [p]
        return packages

    def save(self):
        # create index directories
        for i in [self.index_root] + [self.index_root + '/' + p for p in self.packages.keys()]:
            try:
                os.mkdir(i)
            except OSError:
                pass

        # create root index
        packages = ['<a href="{0}/">{0}</a></br>\n'.format(p) for p in sorted(self.packages.keys())]
        lines = [self.html_header] + packages + [self.html_footer]
        self._write_file(self.index_root + '/index.html', lines)

        # create package indexes
        for package, files in self.packages.iteritems():
            versions = ['<a href="../../{0}">{0}</a></br>\n'.format(p) for p in sorted(files)]
            lines = [self.html_header] + versions + [self.html_footer]
            self._write_file(self.index_root + '/' + package + '/index.html', lines)

    def _write_file(self, filename, lines):
        with open(filename, 'w') as f:
            f.writelines(lines)
