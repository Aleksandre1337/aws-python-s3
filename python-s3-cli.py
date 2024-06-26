# Description: This script is a simple S3 client that can be used to list, create, delete, upload files to S3 buckets and etc. It also has a CLI interface to interact with the S3 client.
# Before running the script, make sure to install the required packages. Also, make sure to set the correct environment variables for the AWS credentials.
# Ensure that you have the required permissions to perform the operations on the S3 buckets. Use this script at your own risk.

import argparse
import boto3
import s3fs
import mimetypes
import os
from os import getenv
from dotenv import load_dotenv
import logging
from botocore.exceptions import ClientError
from hashlib import md5
from time import localtime
from datetime import datetime, timedelta
import pytz
import requests
import random
import json



# Load the environment variables
load_dotenv()

class S3Client:
    # Initialize the S3 client
    def __init__(self):
        self.client = self.init_client()
        self.resource = self.init_resource()

    def init_client(self):
        # Initialize the S3 client
        try:
            client = boto3.client(
                "s3",
                aws_access_key_id=getenv("aws_access_key_id"),
                aws_secret_access_key=getenv("aws_secret_access_key"),
                aws_session_token=getenv("aws_session_token"),
                region_name=getenv("region"))
            client.list_buckets()
            return client
        except ClientError as e:
            logging.error(e)
            raise e
        except Exception as e:
            logging.error("Unexpected Error")
            raise e

    def init_resource(self):
        # Initialize the S3 resource
        try:
            resource = boto3.resource(
                "s3",
                aws_access_key_id=getenv("aws_access_key_id"),
                aws_secret_access_key=getenv("aws_secret_access_key"),
                aws_session_token=getenv("aws_session_token"),
                region_name=getenv("region"))
            return resource
        except ClientError as e:
            logging.error(e)
            raise e
        except Exception as e:
            logging.error("Unexpected Error")
            raise e

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

    def upload_file(self, bucket_name, filename):
        try:
            self.client.upload_file(filename, bucket_name, filename)
            print(f"File uploaded successfully to {bucket_name}")
            return True
        except ClientError as e:
            print(f"An error occurred while uploading the file: {e}")
            return False

    def upload_file_object(self, bucket_name, filename):
        try:
            with open(filename, "rb") as file:
                self.client.upload_fileobj(file, bucket_name, filename)
                print(f"File object uploaded successfully to {bucket_name}")
            return True
        except ClientError as e:
            logging.error(e)
            return False

    def upload_file_put(self, bucket_name, filename):
        try:
            with open(filename, "rb") as file:
                self.client.put_object(Bucket=bucket_name, Key=filename, Body=file.read())
                print(f"File uploaded successfully to {bucket_name}")
            return True
        except ClientError as e:
            logging.error(e)
            return False

    def multipart_upload(self, bucket_name, key, filename):
        mpu = self.client.create_multipart_upload(Bucket=bucket_name, Key=key)
        mpu_id = mpu["UploadId"]
        parts = []
        uploaded_bytes = 0
        total_bytes = os.stat(filename).st_size

        with open(filename, "rb") as file:
            i = 1
            while True:
                data = file.read(1024 * 1024)  # 1MB chunks
                if not len(data):
                    break
                part = self.client.upload_part(Body=data, Bucket=bucket_name, Key=key, UploadId=mpu_id, PartNumber=i)
                parts.append({"PartNumber": i, "ETag": part["ETag"]})
                uploaded_bytes += len(data)
                print("{0} of {1} uploaded".format(uploaded_bytes, total_bytes))
                i += 1
        result = self.client.complete_multipart_upload(
            Bucket=bucket_name, Key=key, UploadId=mpu_id, MultipartUpload={"Parts": parts}
        )
        print(f"File uploaded successfully! Location: {result['Location']}, Bucket: {result['Bucket']}, Key: {result['Key']}, ETag: {result['ETag']}")
        return result

    def download_and_upload(self, bucket_name, url, file_name, keep_local=False):
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
        allowed_mime_types = [
            'image/bmp',
            'image/jpeg',
            'image/png',
            'image/webp',
            'image/svg-xml',
            'image/svg+xml',
            'video/mp4',
            'text/plain',
            'text/html',
            'application/json',
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'audio/mpeg',
            'audio/x-wav',
            'video/x-msvideo',
            'video/quicktime',
            'application/zip',
            'application/x-rar-compressed',
            'application/javascript',
            'text/css',
            'application/xml',
            'application/x-sh',
            'application/x-perl',
            'text/x-python',
            'text/x-php',
            'text/x-ruby',
            'text/x-shellscript',
            'text/x-java-source',
            'application/octet-stream',
            'application/vnd.android.package-archive',
            'application/x-7z-compressed',
            'application/x-tar',
            'application/gzip',
            'application/x-msdownload',
        ]


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

        # Construct the website URL
        location = self.client.get_bucket_location(Bucket=bucket_name)
        region = location['LocationConstraint']
        if region == None:
            region = 'us-east-1'

        s3_url = "https://{0}.s3.{1}.amazonaws.com/{2}".format(bucket_name, region, file_name)
        print(f"The file is available at {s3_url}")
        return s3_url


    def upload_file_to_folder(self, bucket_name, filename):
        import magic
        try:
            mime_type = magic.from_file(filename, mime=True)
            extension = mimetypes.guess_extension(mime_type)
            folder = extension[1:]
            key = f"{folder}/{filename}"
            self.client.upload_file(filename, bucket_name, key)

            print(f"File uploaded successfully to {bucket_name}/{folder}")
            return True
        except ClientError as e:
            print(f"An error occurred while uploading the file: {e}")
            return False

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
        try:
            self.client.delete_public_access_block(Bucket=bucket_name)
            self.client.put_bucket_policy(
                Bucket=bucket_name,
                Policy=self.generate_public_read_policy(bucket_name)
            )
            print(f"Bucket policy created for {bucket_name}")
        except ClientError as e:
            logging.error(e)
            print(f"Error creating bucket policy: {e}")
            return False

    def read_bucket_policy(self, bucket_name):
        try:
            policy = self.client.get_bucket_policy(Bucket=bucket_name)
            policy_str = policy['Policy']
            print(policy_str)
        except ClientError as e:
            logging.error(e)
            print(f"Error reading bucket policy: {e}")
            return False

    def put_lifecycle_config(self, bucketname):
        LifecycleConfiguration = {
            'Rules': [
                {
                    'ID': 'DeleteAfter120Days',
                    'Status': 'Enabled',
                    'Prefix': '',
                    'Expiration': {
                        'Days': 120
                    }
                }
            ]
        }
        try:
            self.client.put_bucket_lifecycle_configuration(
                Bucket=bucketname,
                LifecycleConfiguration=LifecycleConfiguration
            )
            print(f"Lifecycle configuration successfully applied to bucket: {bucketname}")
            return True
        except ClientError as e:
            print(f"Error applying lifecycle configuration to bucket: {bucketname}. Error code: {e.response['Error']['Code']}, Error message: {e.response['Error']['Message']}")
            return False

    def get_lifecycle_config(self, bucketname):
        try:
            response = self.client.get_bucket_lifecycle_configuration(Bucket=bucketname)
            print(response)
            return response
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                print(f"No lifecycle configuration found for bucket: {bucketname}")
            else:
                print(f"Error retrieving lifecycle configuration for bucket: {bucketname}. Error code: {e.response['Error']['Code']}, Error message: {e.response['Error']['Message']}")
            return None

    def manage_s3_object(self, bucket_name, file_name, flag):
        if flag == ':delete':
            try:
                self.client.delete_object(Bucket=bucket_name, Key=file_name)
                print(f"Successfully deleted {file_name} from {bucket_name}")
                return True
            except ClientError as e:
                print(f"Error deleting {file_name} from {bucket_name}. Error: {e}")
                return False
        elif flag == ':download':
            try:
                self.client.download_file(bucket_name, file_name, file_name)
                print(f"Successfully downloaded {file_name} from {bucket_name}")
                return True
            except ClientError as e:
                print(f"Error downloading {file_name} from {bucket_name}. Error: {e}")
                return False
        elif flag == ':versions':
            try:
                versions = self.client.list_object_versions(Bucket=bucket_name, Prefix=file_name)
                print(f'Current versions of {file_name}: \n')
                for version in versions['Versions']:
                    print(f"Version ID: {version['VersionId']}")
                    print(f"  - Size: {version['Size']} bytes")
                    print(f"  - Is Latest: {version['IsLatest']}")
                    print(f"  - Last Modified: {version['LastModified']} UTC")
                    print(f"  - Owner: {version['Owner']['DisplayName']} ({version['Owner']['ID']})")
                    print()
                return True
            except ClientError as e:
                print(f"Error listing versions for {file_name} in {bucket_name}. Error: {e}")
                return False
        elif flag == ':lastversion':
            try:
                versions = self.client.list_object_versions(Bucket=bucket_name, Prefix=file_name)
                if len(versions['Versions']) > 1:
                    last_version = versions['Versions'][1]
                    self.client.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': file_name, 'VersionId': last_version['VersionId']}, Key=file_name)
                    print(f"Successfully uploaded the second last version of {file_name} as the newest in {bucket_name}")
                    return True
                else:
                    print(f"No previous versions found for {file_name} in {bucket_name}")
                    return False
            except ClientError as e:
                print(f"Error uploading the second last version of {file_name} as the newest in {bucket_name}. Error: {e}")
                return False
        elif flag == ':rename':
            try:
                new_name = input("Enter a new name for the object: ")
                self.client.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': file_name}, Key=new_name)
                self.client.delete_object(Bucket=bucket_name, Key=file_name)
                print(f"Successfully renamed {file_name} to {new_name} in {bucket_name}")
                return True
            except ClientError as e:
                print(f"Error renaming {file_name} to {new_name} in {bucket_name}. Error: {e}")
                return False
        elif flag == ':copy':
            try:
                new_name = input("Enter a new name for the copied object: ")
                if new_name == file_name:
                    print("Error: The new name must be different from the original name.")
                    return False
                self.client.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': file_name}, Key=new_name)
                print(f"Successfully copied {file_name} to {new_name} in {bucket_name}")
                return True
            except ClientError as e:
                print(f"Error copying {file_name} to {new_name} in {bucket_name}. Error: {e}")
                return False
        elif flag == ':setversion':
            try:
                response = self.client.list_object_versions(Bucket=bucket_name, Prefix=file_name)
                current_versions = response['Versions']
                version_id = str(input('Enter your desired version ID (leave blank for latest):'))
                if len(version_id) > 0:
                    self.resource.Object(bucket_name, file_name).copy_from(CopySource={'Bucket': bucket_name, 'Key': file_name, 'VersionId': version_id})
                    print(f'The Object {file_name} was successfully updated with version ID {version_id}')
                else:
                    print(f'No version ID was provided, the object {file_name} remains unchanged')
            except ClientError as e:
                print(f"Error setting version for {file_name} in {bucket_name}. Error: {e}")
                return False
        else:
            print("Invalid flag. Please use ':del' to delete, ':copy' to copy, ':down' to download, ':versions' to list versions, or ':lastversion' to upload the second last version as the newest.")
            return False

    def check_versioning(self, bucket_name):
        try:
            response = self.client.get_bucket_versioning(Bucket=bucket_name)
            status = response['Status']
            print(f'Versioning status for {bucket_name}: {status}')
            return status
        except ClientError as e:
            print(f"Error checking versioning status for {bucket_name}. Error: {e}")
            return None

    def manage_versioning(self, bucket_name, flag):
        if flag == 'enable':
            try:
                response = self.client.BucketVersioning(bucket_name).enable()
                print(f"Versioning enabled for {bucket_name}")
                return True
            except ClientError as e:
                print(f"Error: {e}")
                return False
        elif flag == 'suspend':
            try:
                response = self.client.BucketVersioning(bucket_name).suspend()
                print(f"Versioning suspended for {bucket_name}")
                return True
            except ClientError as e:
                print(f"Error: {e}")
                return False

    def rollback_to_first(self, bucket_name, object_key):
        try:
            response = self.client.list_object_versions(Bucket=bucket_name, Prefix=object_key)
            first_version = response['Versions'][0]
            self.resource.Object(bucket_name, object_key).copy_from(CopySource={'Bucket': bucket_name, 'Key': object_key, 'VersionId': first_version.id})
            return True
        except ClientError as e:
            print(f"Error: {e}")
            return False


    def organize_by_extension(self, bucket_name):
        try:
            s3objects = self.client.list_objects(Bucket=bucket_name).get('Contents')

            if not s3objects:
                print("No objects found in the bucket or the bucket does not exist.")
                return False

            # Move each object to the corresponding folder
            for obj in s3objects:
                # Use the file extension (the part after the last dot) as the folder name
                folder = obj['Key'].rsplit('.', 1)[-1]

                new_key = f"{folder}/{obj['Key']}"

                # Check if the object is already in the correct folder
                if not obj['Key'].startswith(folder + '/'):
                    self.client.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': obj['Key']}, Key=new_key)
                    self.client.delete_object(Bucket=bucket_name, Key=obj['Key'])

            print("Successfully organized files into folders based on their file extension")
            return True

        except ClientError as e:
            print(f"An error occurred: {e}")
            return False

    def organize_by_type(self, bucket_name):
        try:
            s3objects = self.client.list_objects(Bucket=bucket_name)['Contents']

            # Move each object to the corresponding folder
            for obj in s3objects:
                obj_metadata = self.client.head_object(Bucket=bucket_name, Key=obj['Key'])
                content_type = obj_metadata['ContentType']

                # Use the main type (the part before the slash) as the folder name
                folder = content_type.split('/')[0]

                new_key = f"{folder}/{obj['Key']}"

                # Check if the object is already in the correct folder
                if not obj['Key'].startswith(folder + '/'):
                    self.client.copy_object(Bucket=bucket_name, CopySource={'Bucket': bucket_name, 'Key': obj['Key']}, Key=new_key)
                    self.client.delete_object(Bucket=bucket_name, Key=obj['Key'])

            print("Successfully organized files into folders based on their content type")
            return True
        except ClientError as e:
            print(f"An error occurred: {e}")
            return False

    def clean_old_versions(self, bucket_name, file_name, day=180):
        try:
            age = datetime.now(pytz.utc) - timedelta(days=day)
            all_objects = self.client.list_object_versions(Bucket=bucket_name, Prefix=file_name)
            versions_to_delete = [{'Key': version['Key'], 'VersionId': version['VersionId']}
                        for version in all_objects.get('Versions', [])
                        if version['LastModified'] < age]
            if versions_to_delete:
                self.client.delete_objects(Bucket=bucket_name, Delete={'Objects': versions_to_delete})
                print(f'Deleted versions of the {file_name} older than {day} days.')
            return True
        except ClientError as e:
            print(f"An error occurred: {e}")
            return False

    def configure_website(self, bucket_name, flag):
        website_configuration = {
        'ErrorDocument': {'Key': 'error.html'},
        'IndexDocument': {'Suffix': 'index.html'},
        }
        if flag == 'get':
            try:
                response = self.client.get_bucket_website(Bucket=bucket_name)
                print(f'Website configuration for {bucket_name}: {response}')
                return response
            except ClientError as e:
                print(f"Error getting the website configuration for {bucket_name}. Error: {e}")
                return False
        elif flag == 'upload':
            try:
                self.client.upload_file('index.html', bucket_name, 'index.html', ExtraArgs={'ContentType': 'text/html'})
                print(f"Successfully uploaded index.html to {bucket_name}")
                self.client.upload_file('error.html', bucket_name, 'error.html', ExtraArgs={'ContentType': 'text/html'})
                print(f"Successfully uploaded error.html to {bucket_name}")
                return True
            except ClientError as e:
                print(f"Error uploading the website configuration for {bucket_name}. Error: {e}")
                return False
        elif flag == 'set':
            try:
                self.client.put_bucket_website(Bucket=bucket_name, WebsiteConfiguration=website_configuration)
                print(f"Successfully set the website configuration for {bucket_name}")
                return True
            except ClientError as e:
                print(f"Error setting the website configuration for {bucket_name}. Error: {e}")
                return False
        elif flag == 'delete':
            try:
                self.client.delete_bucket_website(Bucket=bucket_name)
                print(f"Successfully deleted the website configuration for {bucket_name}")
                return True
            except ClientError as e:
                print(f"Error deleting the website configuration for {bucket_name}. Error: {e}")
                return False

    def print_object_metadata(self, bucket_name, object_key):
        obj_metadata = self.client.head_object(Bucket=bucket_name, Key=object_key)
        print(obj_metadata)

    def generate_quote(self, flag='show'):
        try:
            if flag not in ['show', 'save']:
                print("Invalid flag. Please use 'show' or 'save'.")
                return False
            author = input("Enter the author name: ")
            headers = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
                'accept': 'application/json'
            }
            response = requests.get('https://type.fit/api/quotes', headers=headers)
            quotes = response.json()
            quotes = [quote for quote in quotes if author in quote['author']]

            if not quotes:
                print(f"No quotes found for the specified author: {author}")
                return False

            random_quote = random.choice(quotes)
            output = random_quote['text']

            if flag == 'show':
                print(output)
            elif flag == 'save':
                bucket_name = input("Enter the bucket name to save the quote: ")
                output_json = json.dumps(random_quote)
                output_bytes = output_json.encode('utf-8')
                print(f'Quote: {output}')
                self.client.put_object(Bucket=bucket_name, Key=f"{author}.json", Body=output_bytes)
                print(f"Quote saved to {bucket_name} as {author}.json")
        except Exception as e:
            logging.error(e)

    def create_website(self, bucket_name, sourcedir):
        try:
            # Upload the website source files to the bucket (Preserve Subdirectories)
            for root, dirs, files in os.walk(sourcedir):
                for file in files:
                    local_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(local_file_path, sourcedir)
                    s3_file_path = relative_path.replace(os.sep, '/')  # Replace os.sep with '/' to handle Windows paths

                    # Determine the file's content type
                    content_type = mimetypes.guess_type(file)[0] or 'binary/octet-stream'

                    print(f"Uploading {local_file_path} to {bucket_name}/{s3_file_path}")
                    self.client.upload_file(local_file_path, bucket_name, s3_file_path, ExtraArgs={'ContentType': content_type})

            # Website Configuration
            website_configuration = {
            'IndexDocument': {'Suffix': 'index.html'}
            }
            self.client.put_bucket_website(Bucket=bucket_name, WebsiteConfiguration=website_configuration)
            print(f"Successfully set the website configuration for {bucket_name}")

            # Set Permissions
            policy = {
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/*"
            }]
            }
            self.client.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))
            print(f'Successfully set the bucket policy for {bucket_name}')

            # Construct the website URL
            location = self.client.get_bucket_location(Bucket=bucket_name)
            region = location['LocationConstraint']

            # If the region is None, the bucket is in us-east-1 (Normal System behavior)
            if region is None:
                region = 'us-east-1'
            website_url = f'https://{bucket_name}.s3-website-{region}.amazonaws.com'

            print(f'Your website is hosted at : {website_url}')
        except ClientError as e:
            logging.error(e)
            return False

    def get_file_stats(self, bucket_name):
        file_stats = {}
        try:
            response = self.client.list_objects_v2(Bucket=bucket_name)
            if 'Contents' in response:
                for item in response['Contents']:
                    file_key = item['Key']
                    file_extension = os.path.splitext(file_key)[1][1:]
                    size_bytes = item['Size']

                    if file_extension in file_stats:
                        file_stats[file_extension]['Count'] += 1
                        file_stats[file_extension]['Size'] += size_bytes
                    else:
                        file_stats[file_extension] = {'Count': 1, 'Size': size_bytes}
        except ClientError as e:
            logging.error(e)
            return False
        for stat in file_stats:
            size_kb = file_stats[stat]['Size'] / 1024
            size_mb = file_stats[stat]['Size'] / (1024 * 1024)
            print(f"File extension: {stat}")
            print(f"  - Number of files: {file_stats[stat]['Count']}")
            print(f"  - Total size in bytes: {file_stats[stat]['Size']}")
            print(f"  - Total size in KB: {size_kb}")
            print(f"  - Total size in MB: {'{:.16f}'.format(size_mb)}")

    def get_all_stats(self, bucket_name):
        file_stats = {'Count': 0, 'Size': 0}
        try:
            response = self.client.list_objects_v2(Bucket=bucket_name)
            if 'Contents' in response:
                for item in response['Contents']:
                    file_stats['Count'] += 1
                    file_stats['Size'] += item['Size']
            size_kb = file_stats['Size'] / 1024
            size_mb = file_stats['Size'] / (1024 * 1024)
            print(f'Number of files: {file_stats["Count"]}')
            print(f'Total size in bytes: {file_stats["Size"]}')
            print(f'Total size in KB: {size_kb}')
            print(f"Total size in MB: {'{:.16f}'.format(size_mb)}")
        except ClientError as e:
            logging.error(e)
            return False

    def set_bucket_encryption(self, bucket_name):
        try:
            result = self.client.put_bucket_encryption(
                Bucket=bucket_name,
                ServerSideEncryptionConfiguration={
                    "Rules": [
                        {"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}
                    ]
                },
            )
            status_code = result["ResponseMetadata"]["HTTPStatusCode"]
            if status_code == 200:
                print(f'Encryption enabled for {bucket_name}')
                return True
        except ClientError as e:
            logging.error(e)
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
        parser.add_argument("--download-and-upload", nargs=4, help="Download a file and upload it to S3 (Arguments: bucket_name, url, file_name, keep_local = True or False)")
        parser.add_argument("--set-object-access-policy", nargs=2, help="Set object access policy (Arguments: bucket_name, file_name)")
        parser.add_argument("--generate-public-read-policy", type=str, help="Generate public read policy (Arguments: bucket_name)")
        parser.add_argument("--create-bucket-policy", type=str, help="Create bucket policy (Arguments: bucket_name)")
        parser.add_argument("--read-bucket-policy", type=str, help="Read bucket policy (Arguments: bucket_name)")
        parser.add_argument("--upload-file", type=str, nargs=2, help="Upload a local file to S3 Bucket (Arguments: bucketname, filename)")
        parser.add_argument("--upload-file-object", nargs=2, type=str, help="Upload a local file object to S3 Bucket (Arguments: bucketname, filename)")
        parser.add_argument("--upload-file-put", nargs=2, type=str, help="Upload a local file using the PUT method to S3 Bucket (Arguments: bucketname, filename)")
        parser.add_argument("--put-lifecycle-config", type=str, help="Apply lifecycle configuration to a bucket (Arguments: bucketname)")
        parser.add_argument("--multipart-upload", nargs=3, help="Upload a file to S3 using multipart upload (Arguments: bucketname, key, filename)")
        parser.add_argument("--get-lifecycle-config", type=str, help="Get the lifecycle configuration of a bucket (Arguments: bucketname)")
        parser.add_argument("--manage-s3-object", nargs=3, help="Manage S3 object (Arguments: bucket_name, file_name, flag = :delete, :versions, :download, :lastversion, :rename, :copy, :setversion)", metavar=("bucket_name", "file_name", "flag"))
        parser.add_argument("--check-versioning", type=str, help="Check versioning status of a bucket (Arguments: bucket_name)")
        parser.add_argument("--organize-by-type", type=str, help="Organize files in the bucket based on their content type (Arguments: bucket_name)")
        parser.add_argument('--organize-by-extension', type=str, help='The name of the S3 bucket to organize.')
        parser.add_argument("--print-object-metadata", nargs=2, help="Print metadata of an object in a bucket (Arguments: bucket_name, object_key)")
        parser.add_argument("--upload-file-to-folder", nargs=2, help="Upload a file to a folder in S3 Bucket (Arguments: bucketname, filename")
        parser.add_argument("--clean-old-versions", nargs=3, help="Clean old versions of a file in a bucket (Arguments: bucket_name, filename, day (Default value is 180 days))")
        parser.add_argument("--rollback-to-first", nargs=2, help="Rollback an object in a bucket to its first version (Arguments: bucket_name, object_key)")
        parser.add_argument("--configure-website", nargs=2, help="Configure website for a bucket (Arguments: bucket_name, flag (get, set, upload or delete))", metavar=("bucket_name", "flag"))
        parser.add_argument("--manage-versioning", nargs=2, help="Manage versioning for a bucket (Arguments: bucket_name, flag (enable or suspend))", metavar=("bucket_name", "flag"))
        parser.add_argument("--inspire", nargs='?', const='show', help="Generate and display or save a random quote from the specified author. Use 'show' or 'save'.")
        parser.add_argument("--create-website", nargs=2, help="Create a website in an S3 bucket (Arguments: bucket_name, sourcedirectory)")
        parser.add_argument("--get-file-stats", type=str, help="Get file statistics (Extension) for a bucket (Arguments: bucket_name)")
        parser.add_argument("--get-all-stats", type=str, help="Get all file statistics (Total Size) for a bucket (Arguments: bucket_name)")
        parser.add_argument("--encrypt-bucket", type=str, help="Enable bucket encryption (Arguments: bucket_name)")


        args = parser.parse_args()

        if args.list_buckets:
            print(self.list_buckets())
        elif args.print_object_metadata:
            self.print_object_metadata(args.print_object_metadata[0], args.print_object_metadata[1])
        elif args.upload_file:
            self.upload_file(args.upload_file[0], args.upload_file[1])
        elif args.upload_file_object:
            self.upload_file_object(args.upload_file_object[0], args.upload_file_object[1])
        elif args.upload_file_put:
            self.upload_file_put(args.upload_file_put[0], args.upload_file_put[1])
        elif args.multipart_upload:
            self.multipart_upload(args.multipart_upload[0], args.multipart_upload[1], args.multipart_upload[2])
        elif args.put_lifecycle_config:
            self.put_lifecycle_config(args.put_lifecycle_config)
        elif args.get_lifecycle_config:
            self.get_lifecycle_config(args.get_lifecycle_config)
        elif args.check_versioning:
            self.check_versioning(args.check_versioning)
        elif args.organize_by_extension:
            self.organize_by_extension(args.organize_by_extension)
        elif args.organize_by_type:
            self.organize_by_type(args.organize_by_type)
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
        elif args.download_and_upload:
            self.download_and_upload(args.download_and_upload[0], args.download_and_upload[1], args.download_and_upload[2], args.download_and_upload[3])
        elif args.set_object_access_policy:
            self.set_object_access_policy(args.set_object_access_policy[0], args.set_object_access_policy[1])
        elif args.generate_public_read_policy:
            print(self.generate_public_read_policy(args.generate_public_read_policy))
        elif args.create_bucket_policy:
            self.create_bucket_policy(args.create_bucket_policy)
        elif args.read_bucket_policy:
            self.read_bucket_policy(args.read_bucket_policy)
        elif args.manage_s3_object:
            self.manage_s3_object(args.manage_s3_object[0], args.manage_s3_object[1], args.manage_s3_object[2])
        elif args.upload_file_to_folder:
            self.upload_file_to_folder(args.upload_file_to_folder[0], args.upload_file_to_folder[1])
        elif args.clean_old_versions:
            self.clean_old_versions(args.clean_old_versions[0], args.clean_old_versions[1], int(args.clean_old_versions[2]))
        elif args.rollback_to_first:
            self.rollback_to_first(args.rollback_to_first[0], args.rollback_to_first[1])
        elif args.configure_website:
            self.configure_website(args.configure_website[0], args.configure_website[1])
        elif args.manage_versioning:
            self.manage_versioning(args.manage_versioning[0], args.manage_versioning[1])
        elif args.inspire:
            self.generate_quote(args.inspire)
        elif args.create_website:
            self.create_website(args.create_website[0], args.create_website[1])
        elif args.get_file_stats:
            self.get_file_stats(args.get_file_stats)
        elif args.get_all_stats:
            self.get_all_stats(args.get_all_stats)
        elif args.encrypt_bucket:
            self.set_bucket_encryption(args.encrypt_bucket)

# Run the script
if __name__ == "__main__":
        s3 = S3Client()
        s3.main()
