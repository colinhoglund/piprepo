import boto3
import sys
from moto import mock_s3
from piprepo import command


def test_build(tmpdir):
    sys.argv = ['', 'build', tmpdir.dirname]
    command.main()


@mock_s3
def test_sync(tmpdir):
    bucket = 'fake-piprepo-bucket'
    conn = boto3.resource('s3')
    conn.create_bucket(Bucket=bucket)

    sys.argv = ['', 'sync', tmpdir.dirname, 's3://{}/piprepo'.format(bucket)]
    command.main()
