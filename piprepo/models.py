import abc
import logging
import os
import re
import subprocess
import tempfile


class Index(object):
    ''' Abstract class that defines index interface '''

    __metaclass__ = abc.ABCMeta
    html_header = '<!DOCTYPE html><html><body>\n'
    html_footer = '</body></html>\n'

    def __init__(self, directory):
        self.directory = directory
        self.index_root = directory.rstrip('/') + '/simple'
        self.packages = {}

    @abc.abstractmethod
    def __enter__():
        pass

    @abc.abstractmethod
    def __exit__():
        pass

    def write_html(self):
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

    def build_packages(self):
        files = [f for f in os.listdir(self.directory) if os.path.isfile(self.directory + '/' + f)]
        for p in files:
            name = os.path.basename(p).split('-')[0]
            # normalize name as per https://www.python.org/dev/peps/pep-0503/
            name = re.sub(r"[-_.]+", "-", name).lower()
            if name in self.packages and p not in self.packages[name]:
                self.packages[name].append(p)
            else:
                self.packages[name] = [p]


class RemoteIndex(Index):
    ''' Abstract class that defines remote index interface '''

    __metaclass__ = abc.ABCMeta

    def __init__(self, path):
        self.path = path
        super(RemoteIndex, self).__init__(tempfile.mkdtemp())

    def __enter__(self):
        self.sync_from_remote()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.write_html()
        self.sync_to_remote()

    @abc.abstractmethod
    def sync_from_remote():
        pass

    @abc.abstractmethod
    def sync_to_remote():
        pass


class LocalIndex(Index):
    ''' Context manager for creating an index on the local filesystem '''

    def __init__(self, directory):
        super(LocalIndex, self).__init__(directory)

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.write_html()


class RsyncIndex(RemoteIndex):
    ''' Context manager for creating an index over rsync '''

    def __init__(self, path):
        super(RsyncIndex, self).__init__(path)

    def sync_from_remote(self):
        try:
            subprocess.check_call(['rsync', '-a', self.path.rstrip('/') + '/', self.directory + '/'])
            self.build_packages()
        except subprocess.CalledProcessError:
            logging.info('Remote index does not exist, creating...')

    def sync_to_remote(self):
        subprocess.check_call(['rsync', '-a', self.directory + '/', self.path.rstrip('/') + '/'])


class S3Index(RemoteIndex):
    ''' Context manager for creating an index in AWS S3 '''

    def __init__(self, path):
        super(S3Index, self).__init__(path)
