import sys
from piprepo import command


def test_no_options(tmpdir):
    sys.argv = ['', tmpdir.dirname, 'pytest']
    command.main()


def test_get_source_and_build_wheels(tmpdir):
    sys.argv = ['', '-sw', tmpdir.dirname, 'pytest']
    command.main()
