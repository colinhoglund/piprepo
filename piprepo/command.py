import argparse
import logging
from piprepo import __description__
from piprepo import models


def build(args):
    ''' build sub-command function for building local indexes '''

    with models.LocalIndex(args.directory, args.directory):
        logging.info('Building index in {}'.format(args.directory))


def sync(args):
    ''' sync sub-command function for building and syncing indexes '''

    if args.destination.startswith('s3://'):
        index_type = models.S3Index
    else:
        index_type = models.LocalIndex

    with index_type(args.source, args.destination):
        logging.info('Syncing index in {} to {}'.format(args.source, args.destination))


def main():
    ''' command line entry point and argument parser '''

    parser = argparse.ArgumentParser(description=__description__)
    subparsers = parser.add_subparsers(title='subcommands', dest='subcommands')
    subparsers.required = True

    build_parser = subparsers.add_parser('build')
    build_parser.add_argument('directory', help='Local directory to build')
    build_parser.set_defaults(func=build)

    sync_parser = subparsers.add_parser('sync')
    sync_parser.add_argument('source', help='Repository source')
    sync_parser.add_argument('destination', help='Repository destination')
    sync_parser.set_defaults(func=sync)

    args = parser.parse_args()
    args.func(args)
