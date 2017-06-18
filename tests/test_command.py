import boto3
import os
import pytest
import re
import shutil
import sys
import tempfile
from botocore.exceptions import ClientError
from moto import mock_s3
from piprepo import command


# Fixtures
@pytest.yield_fixture(scope="function")
def tempindex():
    temp = tempfile.mkdtemp()
    index = {
        'wheels': [
            'fake_package-1.0.0-py2.py3-none-any.whl',
            'fake_package-2.0.0-py2.py3-none-any.whl',
            'fake_package2-2.0.0-py2.py3-none-any.whl',
        ],
        'source': os.path.join(temp, 'source'),
        'destination': os.path.join(temp, 'destination'),
    }
    os.mkdir(index['source'])
    os.mkdir(index['destination'])
    for wheel in index['wheels']:
        with open(os.path.join(index['source'], wheel), 'w') as f:
            f.write(wheel)
    yield index
    shutil.rmtree(temp)


@pytest.yield_fixture(scope="function")
def s3_conn():
    mock_s3().start()
    resource = boto3.resource('s3', region_name='us-east-1')
    yield resource
    mock_s3().stop()


# Tests
def test_build(tempindex):
    sys.argv = ['', 'build', tempindex['source']]
    command.main()

    for wheel in tempindex['wheels']:
        source_file = os.path.join(tempindex['source'], wheel)
        index = os.path.join(tempindex['source'], 'simple', get_pep503_package_name(wheel), 'index.html')
        assert os.path.isfile(source_file)
        assert os.path.isfile(index)
        with open(os.path.join(tempindex['source'], 'simple', 'index.html')) as f:
            assert get_pep503_package_name(wheel) in f.read()
        with open(index, 'r') as f:
            assert wheel in f.read()


def test_dir_sync(tempindex):
    sys.argv = ['', 'sync', tempindex['source'], tempindex['destination']]
    command.main()

    for wheel in tempindex['wheels']:
        dest_file = os.path.join(tempindex['destination'], wheel)
        dest_index = os.path.join(tempindex['destination'], 'simple', get_pep503_package_name(wheel), 'index.html')
        assert os.path.isfile(dest_file)
        assert os.path.isfile(dest_index)
        with open(os.path.join(tempindex['destination'], 'simple', 'index.html')) as f:
            assert get_pep503_package_name(wheel) in f.read()
        with open(dest_index, 'r') as f:
            assert wheel in f.read()


def test_s3_sync(tempindex, s3_conn):
    bucket = s3_conn.create_bucket(Bucket='fake-piprepo-bucket')
    sys.argv = ['', 'sync', tempindex['source'], 's3://{}/piprepo'.format(bucket.name)]
    command.main()

    for wheel in tempindex['wheels']:
        package = s3_conn.Object(bucket.name, os.path.join('piprepo', wheel))
        package_index = s3_conn.Object(
            bucket.name, os.path.join('piprepo', 'simple', get_pep503_package_name(wheel), 'index.html')
        )
        root_index = s3_conn.Object(bucket.name, os.path.join('piprepo', 'simple', 'index.html'))

        assert s3_object_exists(package)
        assert s3_object_exists(package_index)
        assert s3_object_exists(root_index)
        assert get_pep503_package_name(wheel).encode() in root_index.get()['Body'].read()
        assert wheel.encode() in package_index.get()['Body'].read()


def s3_object_exists(obj):
    try:
        obj.load()
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            raise
    return True


def get_pep503_package_name(filename):
    ''' get PEP-503 normalized name '''
    return re.sub(r"[-_.]+", "-", os.path.basename(filename).split('-')[0]).lower()
