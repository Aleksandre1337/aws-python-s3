# Description: This script is a simple S3 client that can be used to list, create, delete, and upload files to S3 buckets. It also has a CLI interface to interact with the S3 client.
# Before running the script, make sure to install the required packages. Also, make sure to set the correct environment variables for the AWS credentials.
# Ensure that you have the required permissions to perform the operations on the S3 buckets. Use this script at your own risk.

import argparse
import boto3
from os import getenv
from dotenv import load_dotenv
import logging
from botocore.exceptions import ClientError
from hashlib import md5
from time import localtime

# Load the environment variables
load_dotenv()

class S3Client:
    # Initialize the S3 client
    def __init__(self):
        self.client = self.init_client()

    def init_client(self):
      # Initialize the S3 client
        try:
            client = boto3.client(
                "s3",
                aws_access_key_id=getenv("aws_access_key_id"),
                aws_secret_access_key=getenv("aws_secret_access_key"),
                aws_session_token=getenv("aws_session_token"),
                region_name=getenv("region_name"))
            client.list_buckets()
            return client
        except ClientError as e:
            logging.error(e)
        except:
            logging.error("Unexpected Error")

    def list_buckets(self):
        # List all of the available buckets
        try:
            return self.client.list_buckets()
        except ClientError as e:
            logging.error(e)
            return False

    def list_bucket_names(self):
      # List all of the available bucket names
      buckets = self.list_buckets()
      if buckets:
          for bucket in buckets['Buckets']:
              print(f'Bucket Name: {bucket["Name"]} and Creation Date : {bucket["CreationDate"]}\n')

    def delete_bucket(self, bucket_name):
    # Delete the S3 bucket
        try:
            self.client.delete_bucket(Bucket=bucket_name)
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketNotEmpty':
                print(f'Bucket {bucket_name} could not be deleted because it is not empty.')
            else:
                logging.error(e)
            return False
        print(f'Successfully deleted bucket {bucket_name}.')
        return True

    def create_bucket(self, bucket_name, region='us-west-2'):
        # Create the S3 bucket
        try:
            location = {'LocationConstraint': region}
            if self.client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location):
                print(f'Successfully created bucket {bucket_name}.')
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def create_multiple_buckets(self, bucket_name, first_index, last_index):
        # Create a list of bucket names
        bucket_name_list = [bucket_name + "-" + str(i) for i in range(first_index, last_index + 1)]
        # Create the buckets according to the list
        for bucket in bucket_name_list:
            try:
                self.create_bucket(bucket)
            except ClientError as e:
                logging.error(e)
                print(f'Failed to create bucket {bucket}.')
                return False
        return True

    def delete_all_buckets(self):
        # Get the names of the buckets
        names = [name['Name'] for name in self.list_buckets()['Buckets']]
        # Delete all buckets
        for bucket in names:
            try:
                self.delete_bucket(bucket)
            except ClientError as e:
                logging.error(e)
                return False
        return True

    def bucket_exists(self, bucket_name):
        try:
            response = self.client.head_bucket(Bucket=bucket_name)
            statuscode = response['ResponseMetadata']['HTTPStatusCode']
            print(f'S3 Bucket: {bucket_name} || Status: Exists || HTTP Status Code: {statuscode}')
        except ClientError as e:
            errorcode = e.response['Error']['Code']
            #logging.error(e)
            print(f'S3 Bucket: {bucket_name} || Status: Does not exist || Error Code: {errorcode}')
            return False
        statuscode = response['ResponseMetadata']['HTTPStatusCode']
        if statuscode == 200:
              return True
        return False



    def download_file_and_upload_to_s3(self, bucket_name, url, file_name, keep_local=False):
        import filetype
        from urllib.request import urlopen, Request
        import io
        # Download the file from the URL
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        request = Request(url=url, headers=headers)
        with urlopen(request) as response:
            content = response.read()

        # Detect the MIME type of the content
        kind = filetype.guess(content)
        if kind is not None:
            mime_type = kind.mime
        else:
            mime_type = None

        # List of allowed MIME types
        allowed_mime_types = ['image/bmp', 'image/jpeg', 'image/png', 'image/webp', 'video/mp4']

        if mime_type not in allowed_mime_types:
            print(f"File type not allowed: {mime_type}")
            return None

        try:
            self.client.upload_fileobj(io.BytesIO(content), Bucket=bucket_name, Key=file_name)
        except Exception as e:
            logging.error(f"Error uploading file to S3: {e}")

        if keep_local:
            with open(file_name, 'wb') as my_file:
                my_file.write(content)

        s3_url = "https://s3-{0}.amazonaws.com/{1}/{2}".format('us-west-2', bucket_name, file_name)
        print(f"The file is available at {s3_url}")
        return s3_url

    def set_object_access_policy(self, bucket_name, file_name):
        try:
            response = self.client.put_object_acl(
                ACL='public-read',
                Bucket=bucket_name,
                Key=file_name
            )
            status_code = response['ResponseMetadata']['HTTPStatusCode']
            if status_code == 200:
                print(f'Successfully set read access for {file_name} in {bucket_name}.')
                return True
            else:
                print(f'Failed to set read access for {file_name} in {bucket_name}. HTTP status code: {status_code}')
                return False
        except ClientError as e:
            logging.error(e)
            print(f'Error setting read access for {file_name} in {bucket_name}. Error: {e}')
            return False

    def generate_public_read_policy(self, bucket_name):
        import json
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        return json.dumps(policy)

    def create_bucket_policy(self, bucket_name):
        self.client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=self.generate_public_read_policy(bucket_name)
        )
        print(f"Bucket policy created for {bucket_name}")

    def read_bucket_policy(self, bucket_name):
        try:
            policy = self.client.get_bucket_policy(Bucket=bucket_name)
            policy_str = policy['Policy']
            print(policy_str)
        except ClientError as e:
            logging.error(e)
            print(f"Error reading bucket policy: {e}")
            return False

    # CLI functions with argparse
    def main(self):
        parser = argparse.ArgumentParser(description="S3 Client")
        parser.add_argument("--list-buckets", action="store_true", help="List all available buckets (Full Body Response)")
        parser.add_argument("--list-bucket-names", action="store_true", help="List all available bucket names")
        parser.add_argument("--delete-bucket", type=str, help="Delete the specified bucket (Arguments: name)")
        parser.add_argument("--create-bucket", type=str, help="Create a new bucket (Arguments: name)")
        parser.add_argument("--create-multiple-buckets", nargs=3, help="Create multiple buckets (Arguments: name, first_index, last_index)")
        parser.add_argument("--delete-all-buckets", action="store_true", help="Delete all buckets")
        parser.add_argument("--bucket-exists", type=str, help="Check if the bucket exists (Arguments: bucket_name)")
        parser.add_argument("--download-file-and-upload-to-s3", nargs=4, help="Download a file and upload it to S3 (bucket_name, url, file_name, keep_local = True or False)")
        parser.add_argument("--set-object-access-policy", nargs=2, help="Set object access policy (Arguments: bucket_name, file_name)")
        parser.add_argument("--generate-public-read-policy", type=str, help="Generate public read policy (Arguments: bucket_name)")
        parser.add_argument("--create-bucket-policy", type=str, help="Create bucket policy (Arguments: bucket_name)")
        parser.add_argument("--read-bucket-policy", type=str, help="Read bucket policy (Arguments: bucket_name)")

        args = parser.parse_args()

        if args.list_buckets:
            print(self.list_buckets())
        elif args.list_bucket_names:
            self.list_bucket_names()
        elif args.delete_bucket:
            self.delete_bucket(args.delete_bucket)
        elif args.create_bucket:
            self.create_bucket(args.create_bucket)
        elif args.create_multiple_buckets:
            self.create_multiple_buckets(args.create_multiple_buckets[0], int(args.create_multiple_buckets[1]), int(args.create_multiple_buckets[2]))
        elif args.delete_all_buckets:
            self.delete_all_buckets()
        elif args.bucket_exists:
            self.bucket_exists(args.bucket_exists)
        elif args.download_file_and_upload_to_s3:
            self.download_file_and_upload_to_s3(args.download_file_and_upload_to_s3[0], args.download_file_and_upload_to_s3[1], args.download_file_and_upload_to_s3[2], args.download_file_and_upload_to_s3[3])
        elif args.set_object_access_policy:
            self.set_object_access_policy(args.set_object_access_policy[0], args.set_object_access_policy[1])
        elif args.generate_public_read_policy:
            print(self.generate_public_read_policy(args.generate_public_read_policy))
        elif args.create_bucket_policy:
            self.create_bucket_policy(args.create_bucket_policy)
        elif args.read_bucket_policy:
            self.read_bucket_policy(args.read_bucket_policy)

# Run the script
if __name__ == "__main__":
    s3 = S3Client()
    s3.main()

