import argparse
import pip
import tempfile
from piprepo import __description__
from piprepo.models import Index


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
