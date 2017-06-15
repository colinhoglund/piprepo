import argparse
import os
import pip
import piprepo
import re
import tempfile


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
        indexes = [self.index_root] + [self.index_root + '/' + p for p in self.packages.keys()]
        for i in indexes:
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


def parse_args():
    ''' Sets up argparse and returns a tuple of (piprepo_args, pip_args) '''

    usage = '''
  piprepo [-hsw] target [pip_options] packages
  piprepo [-hsw] target [pip_options] -r requirements_file'''

    parser = argparse.ArgumentParser(
        description=piprepo.__description__,
        usage=usage
    )
    parser.add_argument('target', help='Repository target')
    parser.add_argument('-s', '--get-source',
                        default=False, action='store_true',
                        help='Download source tarballs')
    parser.add_argument('-w', '--build-wheels',
                        default=False, action='store_true',
                        help='Build wheels from source packages')

    return parser.parse_known_args()


def get_working_directory(target):
    ''' Returns temporary working directory for remote targets '''
    if target.startswith('s3://'):
        return tempfile.mkdtemp()
    elif target.startswith('rsync://'):
        return tempfile.mkdtemp()
    return target


def main():
    args, pip_args = parse_args()
    working_directory = get_working_directory(args.target)

    # let index decide what to download unless forcing wheels and tarballs
    if not (args.get_source and args.build_wheels):
        pip.main(['download', '-d', working_directory] + pip_args)
    # download source tarballs only
    if args.get_source:
        pip.main(['download', '-d', working_directory, '--no-binary', ':all:'] + pip_args)
    # download/compile wheels only
    if args.build_wheels:
        pip.main(['wheel', '--wheel-dir', working_directory] + pip_args)

    # create index and write index files
    Index(working_directory).save()

    # TODO: publish to remote targets
