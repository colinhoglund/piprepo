import argparse
import pip
from piprepo import __description__
from piprepo import models


def parse_args():
    ''' Sets up argparse and returns a tuple of (piprepo_args, pip_args) '''

    usage = '''
  piprepo [-hsw] target [pip_options] packages
  piprepo [-hsw] target [pip_options] -r requirements_file'''

    parser = argparse.ArgumentParser(
        description=__description__,
        usage=usage
    )
    parser.add_argument('target', help='Repository target')
    parser.add_argument('-s', '--get-source',
                        default=False, action='store_true',
                        help='Download source tarballs')
    parser.add_argument('-w', '--build-wheels',
                        default=False, action='store_true',
                        help='Build wheels from source packages')
    parser.add_argument('-r', '--remote', choices=['rsync', 's3'],
                        help='Sync index to a remote target')

    return parser.parse_known_args()


def get_index_class(target_type):
    ''' Returns index class based on remote target type '''
    if target_type == 's3':
        return models.S3Index
    elif target_type == 'rsync':
        return models.RsyncIndex
    return models.LocalIndex


def main():
    args, pip_args = parse_args()

    with get_index_class(args.remote)(args.target) as index:
        # let index decide what to download unless forcing wheels and tarballs
        if not (args.get_source and args.build_wheels):
            pip.main(['download', '-d', index.directory] + pip_args)
        # download source tarballs only
        if args.get_source:
            pip.main(['download', '-d', index.directory, '--no-binary', ':all:'] + pip_args)
        # download/compile wheels only
        if args.build_wheels:
            pip.main(['wheel', '--wheel-dir', index.directory] + pip_args)

        index.build_packages()
