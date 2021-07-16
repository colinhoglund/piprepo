import abc
import errno
import filecmp
import logging
import os
from shutil import copyfile
from piprepo.utils import get_project_name_from_file
from piprepo.exceptions import InvalidFileName
try:
    # python3
    from urllib.parse import urlparse
except ImportError:
    # python2
    from urlparse import urlparse


class Index(object):
    ''' Abstract index class '''
    __metaclass__ = abc.ABCMeta

    html_header = '<!DOCTYPE html><html><body>\n'
    html_root_anchor = '<a href="{0}/">{0}</a></br>\n'
    html_package_anchor = '<a href="../../{0}">{0}</a></br>\n'
    html_footer = '</body></html>\n'

    def __init__(self, source, destination):
        self.source = source.rstrip('/')
        self.destination = destination.rstrip('/')
        self.packages = {}

    @abc.abstractmethod
    def build_source_packages():
        'This method should update the packages dict from the source'

    @abc.abstractmethod
    def build_destination_packages():
        'This method should update the packages dict from the destination'

    @abc.abstractmethod
    def sync_to_destination():
        'This method should sync changes from source to destination'

    def __enter__(self):
        self.build_source_packages()
        if self.source != self.destination:
            self.build_destination_packages()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.create_html_indexes(self.source)
        if self.source != self.destination:
            self.sync_to_destination()

    def build_local_packages(self, directory):
        self._build_packages([
            f for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f)) and
            not f.startswith('.')
        ])

    def create_html_indexes(self, directory):
        index_root = os.path.join(directory, 'simple')
        # create index directories
        for i in [index_root] + [os.path.join(index_root, p) for p in self.packages.keys()]:
            self._create_directory(i)

        # create root index
        packages = [self.html_root_anchor.format(p) for p in sorted(self.packages.keys())]
        lines = [self.html_header] + packages + [self.html_footer]
        self._write_file(os.path.join(index_root, 'index.html'), lines)

        # create package indexes
        for package, files in self.packages.items():
            versions = [self.html_package_anchor.format(p) for p in sorted(files)]
            lines = [self.html_header] + versions + [self.html_footer]
            self._write_file(os.path.join(index_root, package, 'index.html'), lines)

    # hidden helper methods
    def _build_packages(self, packages):
        for package in packages:
            try:
                project = get_project_name_from_file(package)
            except InvalidFileName:
                logging.warning('Skipping invalid file {}'.format(package))
                continue
            if project in self.packages and package not in self.packages[project]:
                self.packages[project].append(package)
            elif project not in self.packages:
                self.packages[project] = [package]

    def _create_directory(self, directory):
        try:
            os.makedirs(directory)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(directory):
                pass

    def _write_file(self, filename, lines):
        with open(filename, 'w') as f:
            f.writelines(lines)


class LocalIndex(Index):
    ''' Base context manager for building local indexes '''

    def build_source_packages(self):
        self.build_local_packages(self.source)

    def build_destination_packages(self):
        self._create_directory(self.destination)
        self.build_local_packages(self.destination)

    def sync_to_destination(self):
        source_walk = [path.rstrip('/') + '/' + f for path, _, files in os.walk(self.source) for f in files]
        for src_file in source_walk:
            dest_file = src_file.replace(src_file[src_file.index(self.source):len(self.source)], self.destination)
            if not os.path.exists(dest_file) or not filecmp.cmp(src_file, dest_file):
                self._create_directory(os.path.dirname(dest_file))
                copyfile(src_file, dest_file)

