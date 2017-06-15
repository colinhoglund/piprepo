import abc
import boto3
import errno
import logging
import os
import re
import subprocess
import tempfile
try:
    # python3
    from urllib.parse import urlparse
except ImportError:
    # python2
    from urlparse import urlparse


class Index(object):
    ''' Abstract class that defines index interface '''

    __metaclass__ = abc.ABCMeta
    html_header = '<!DOCTYPE html><html><body>\n'
    html_footer = '</body></html>\n'

    def __init__(self, directory):
        self.directory = directory.rstrip('/') + '/'
        self.index_root = directory.rstrip('/') + '/simple/'
        self.packages = {}

    @abc.abstractmethod
    def __enter__():
        pass

    @abc.abstractmethod
    def __exit__():
        pass

    def write_html(self):
        # create index directories
        for i in [self.index_root] + [self.index_root + p for p in self.packages.keys()]:
            self._create_directory(i)

        # create root index
        packages = ['<a href="{0}/">{0}</a></br>\n'.format(p) for p in sorted(self.packages.keys())]
        lines = [self.html_header] + packages + [self.html_footer]
        self._write_file(self.index_root + 'index.html', lines)

        # create package indexes
        for package, files in self.packages.items():
            versions = ['<a href="../../{0}">{0}</a></br>\n'.format(p) for p in sorted(files)]
            lines = [self.html_header] + versions + [self.html_footer]
            self._write_file(self.index_root + package + '/index.html', lines)

    def _create_directory(self, directory):
        try:
            os.makedirs(directory)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(directory):
                pass

    def _write_file(self, filename, lines):
        with open(filename, 'w') as f:
            f.writelines(lines)

    def build_packages(self):
        files = [f for f in os.listdir(self.directory) if os.path.isfile(self.directory + f)]
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


# Not sure this class is necessary, should probably just use rsync outside of piprepo
class RsyncIndex(RemoteIndex):
    ''' Context manager for creating an index over rsync '''

    def __init__(self, path):
        self.path = path.rstrip('/') + '/'
        super(RsyncIndex, self).__init__(path)

    def sync_from_remote(self):
        try:
            subprocess.check_call(['rsync', '-a', self.path, self.directory])
            self.build_packages()
        except subprocess.CalledProcessError:
            logging.info('Remote index does not exist, creating...')

    def sync_to_remote(self):
        subprocess.check_call(['rsync', '-a', self.directory, self.path])


class S3Index(RemoteIndex):
    ''' Context manager for creating an index in AWS S3 '''
    conn = boto3.resource('s3')

    def __init__(self, url):
        parsed_url = urlparse(url)
        self.bucket = self.conn.Bucket(parsed_url.netloc)
        self.prefix = parsed_url.path.strip('/') + '/'
        super(S3Index, self).__init__(url)

    def sync_from_remote(self):
        for o in self.bucket.objects.filter(Prefix=self.prefix):
            filename = self.directory + o.Object().key.split(self.prefix)[1]
            self._create_directory(os.path.dirname(filename))
            o.Object().download_file(filename)

    def sync_to_remote(self):
        files = [path.rstrip('/') + '/' + f for path, _, files in os.walk(self.directory) for f in files]
        for f in files:
            key = self.prefix + f.split(self.directory)[1]
            body = open(f, 'rb')
            self.bucket.put_object(Key=key, Body=body)
