import boto3
import errno
# import logging
import os
import re
# import subprocess
try:
    # python3
    from urllib.parse import urlparse
except ImportError:
    # python2
    from urlparse import urlparse


class Index(object):
    ''' Base context manager for building local indexes '''

    html_header = '<!DOCTYPE html><html><body>\n'
    html_footer = '</body></html>\n'

    def __init__(self, directory):
        self.directory = directory.rstrip('/') + '/'
        self.index_root = directory.rstrip('/') + '/simple/'
        self.packages = {}

    def __enter__(self):
        self.build_local_packages()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.write_html()

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

    def build_local_packages(self):
        self._build_packages([
            f for f in os.listdir(self.directory)
            if os.path.isfile(self.directory + f) and
            not f.startswith('.')
        ])

    def _build_packages(self, packages):
        for p in packages:
            name = os.path.basename(p).split('-')[0]
            # normalize name as per https://www.python.org/dev/peps/pep-0503/
            name = re.sub(r"[-_.]+", "-", name).lower()
            if name in self.packages and p not in self.packages[name]:
                self.packages[name].append(p)
            else:
                self.packages[name] = [p]


class S3Index(Index):
    ''' Context manager for creating an index in AWS S3 '''
    conn = boto3.resource('s3')

    def __init__(self, source, url):
        super(S3Index, self).__init__(source)
        parsed_url = urlparse(url)
        self.bucket = self.conn.Bucket(parsed_url.netloc)
        self.prefix = parsed_url.path.strip('/') + '/'

    def __enter__(self):
        self.build_local_packages()
        self.sync_from_remote()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.write_html()
        self.sync_to_remote()

    def sync_from_remote(self):
        s3_packages = [os.path.basename(o.key)
                       for o in self.bucket.objects.filter(Prefix=self.prefix)
                       if 'html' not in o.key]
        self._build_packages(s3_packages)

    def sync_to_remote(self):
        files = [
            path.rstrip('/') + '/' + f
            for path, _, files in os.walk(self.directory)
            for f in files
            if not f.startswith('.')
        ]
        for f in [f for f in files if f.endswith('html')]:
            self._put_object(f, 'text/html')
        for f in [f for f in files if not f.endswith('html')]:
            self._put_object(f, 'binary/octet-stream')

    def _put_object(self, filename, content_type):
        key = self.prefix + filename.split(self.directory)[1]
        body = open(filename, 'rb')
        self.bucket.put_object(Key=key, Body=body, ContentType=content_type)
