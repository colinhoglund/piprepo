import boto3
import os
import pytest
import shutil
import sys
import tempfile
from botocore.exceptions import ClientError
from moto import mock_s3
from piprepo import command
from piprepo.utils import normalize


# Fixtures
@pytest.yield_fixture(scope="function")
def tempindex():
    temp = tempfile.mkdtemp()
    index = {
        'packages': [
            'Django-1.11.2-py2.py3-none-any.whl',
            'ansible-2.0.0.0.tar.gz',
            'ansible-2.3.1.0.tar.gz',
            'python_http_client-2.2.1-py2.py3-none-any.whl',
        ],
        'source': os.path.join(temp, 'source'),
        'destination': os.path.join(temp, 'destination'),
    }
    os.mkdir(index['source'])
    os.mkdir(index['destination'])
    for package in index['packages']:
        with open(os.path.join(index['source'], package), 'w') as f:
            f.write(package)
    yield index
    shutil.rmtree(temp)


# Tests
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
        index = os.path.join(tempindex['source'], 'simple', normalize(package), 'index.html')
        assert os.path.isfile(source_file)
        assert os.path.isfile(index)
        with open(os.path.join(tempindex['source'], 'simple', 'index.html')) as f:
            assert normalize(package) in f.read()
        with open(index, 'r') as f:
            assert package in f.read()


def test_dir_sync(tempindex):
    sys.argv = ['', 'sync', tempindex['source'], tempindex['destination']]
    command.main()

    for package in tempindex['packages']:
        dest_file = os.path.join(tempindex['destination'], package)
        dest_index = os.path.join(tempindex['destination'], 'simple', normalize(package), 'index.html')
        assert os.path.isfile(dest_file)
        assert os.path.isfile(dest_index)
        with open(os.path.join(tempindex['destination'], 'simple', 'index.html')) as f:
            assert normalize(package) in f.read()
        with open(dest_index, 'r') as f:
            assert package in f.read()


@mock_s3
def test_s3_sync(tempindex):
    conn = boto3.resource("s3")
    bucket = conn.create_bucket(Bucket='fake-piprepo-bucket')
    sys.argv = ['', 'sync', tempindex['source'], 's3://{}/piprepo'.format(bucket.name)]
    command.main()

    for package in tempindex['packages']:
        package_obj = conn.Object(bucket.name, os.path.join('piprepo', package))
        package_index_obj = conn.Object(
            bucket.name, os.path.join('piprepo', 'simple', normalize(package), 'index.html')
        )
        root_index_obj = conn.Object(bucket.name, os.path.join('piprepo', 'simple', 'index.html'))

        assert s3_object_exists(package_obj)
        assert s3_object_exists(package_index_obj)
        assert s3_object_exists(root_index_obj)
        assert normalize(package).encode() in root_index_obj.get()['Body'].read()
        assert package.encode() in package_index_obj.get()['Body'].read()


def s3_object_exists(obj):
    try:
        obj.load()
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            raise
    return True
