import boto3
import os
from botocore.exceptions import ClientError
from moto import mock_s3
from piprepo.models import S3Index
from piprepo.utils import get_project_name_from_file
from .conftest import PACKAGES


def assert_s3_bucket_contents(conn, bucket, prefix=''):
    for package in PACKAGES:
        package_obj = conn.Object(bucket.name, os.path.join(prefix, package))
        package_index_obj = conn.Object(
            bucket.name, os.path.join(prefix, 'simple', get_project_name_from_file(package), 'index.html')
        )
        root_index_obj = conn.Object(bucket.name, os.path.join(prefix, 'simple', 'index.html'))

        assert s3_object_exists(package_obj)
        assert s3_object_exists(package_index_obj)
        assert s3_object_exists(root_index_obj)
        assert get_project_name_from_file(package).encode() in root_index_obj.get()['Body'].read()
        assert package.encode() in package_index_obj.get()['Body'].read()


@mock_s3
def assert_s3_sync(source, destination):
    conn = boto3.resource("s3")
    bucket = conn.create_bucket(Bucket='piprepo')
    index = S3Index(source, destination)
    with index:
        pass
    assert_s3_bucket_contents(conn, bucket, index.prefix)


def test_s3_sync_with_prefix(tempindex):
    assert_s3_sync(tempindex['source'], 's3://piprepo/prefix')


def test_s3_sync_with_prefix_trailing_slash(tempindex):
    assert_s3_sync(tempindex['source'] + '/', 's3://piprepo/prefix/')


def test_s3_sync_without_prefix(tempindex):
    assert_s3_sync(tempindex['source'], 's3://piprepo')


def test_s3_sync_without_prefix_trailing_slash(tempindex):
    assert_s3_sync(tempindex['source'] + '/', 's3://piprepo/')


def s3_object_exists(obj):
    try:
        obj.load()
    except ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False
        else:
            raise
    return True
