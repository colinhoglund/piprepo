import boto3
import sys
from moto import mock_s3
from piprepo import command


def test_build(tmpdir):
    sys.argv = ['', 'build', tmpdir.dirname]
    command.main()


def test_dir_sync(tmpdir):
    dir1 = tmpdir.mkdir('dir1')
    dir2 = tmpdir.mkdir('dir2')
    sys.argv = ['', 'sync', dir1.dirname, dir2.dirname]
    command.main()


@mock_s3
def test_s3_sync(tmpdir):
    bucket = 'fake-piprepo-bucket'
    conn = boto3.resource('s3')
    conn.create_bucket(Bucket=bucket)

    sys.argv = ['', 'sync', tmpdir.dirname, 's3://{}/piprepo'.format(bucket)]
    command.main()
