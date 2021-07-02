import boto3
import os
import pytest
import sys
from moto import mock_s3
from piprepo import command
from piprepo.utils import get_project_name_from_file, get_yank_reason_package_tag
from .test_s3 import assert_s3_bucket_contents


def test_bare_command():
    with pytest.raises(SystemExit) as ex:
        sys.argv = ['piprepo']
        command.main()
        assert 'usage: piprepo' in ex.message


def test_build(tempindex):
    sys.argv = ['', 'build', tempindex['source']]
    command.main()

    for package in tempindex['packages']:
        source_file = os.path.join(tempindex['source'], package)
        index = os.path.join(tempindex['source'], 'simple', get_project_name_from_file(package), 'index.html')
        assert os.path.isfile(source_file)
        assert os.path.isfile(index)
        with open(os.path.join(tempindex['source'], 'simple', 'index.html')) as f:
            assert get_project_name_from_file(package) in f.read()
        with open(index, 'r') as f:
            package_version_list = f.read()
            assert package in package_version_list
            if package + '.yank' in tempindex['yanked_packages'].keys():
                assert get_yank_reason_package_tag(package, tempindex['yanked_packages'][package + '.yank']) in package_version_list


def test_dir_sync(tempindex):
    sys.argv = ['', 'sync', tempindex['source'], tempindex['destination']]
    command.main()

    for package in tempindex['packages']:
        dest_file = os.path.join(tempindex['destination'], package)
        dest_index = os.path.join(tempindex['destination'], 'simple', get_project_name_from_file(package), 'index.html')
        assert os.path.isfile(dest_file)
        assert os.path.isfile(dest_index)
        with open(os.path.join(tempindex['destination'], 'simple', 'index.html')) as f:
            assert get_project_name_from_file(package) in f.read()
        with open(dest_index, 'r') as f:
            assert package in f.read()


@mock_s3
def test_s3_sync(tempindex):
    conn = boto3.resource("s3")
    bucket = conn.create_bucket(Bucket='piprepo')
    sys.argv = ['', 'sync', tempindex['source'], 's3://{}'.format(bucket.name)]
    command.main()

    assert_s3_bucket_contents(conn, bucket)
