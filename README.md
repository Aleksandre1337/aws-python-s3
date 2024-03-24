# AWS S3 Client

This S3 Client provides a variety of features for managing AWS S3 buckets and objects. While the current functionality includes operations such as listing, creating, and deleting buckets, as well as uploading files and managing access policies, you might see more features added to enhance the tool's capabilities.

## Installation

Before running the script, make sure to install the required packages. You can install them using pip or poetry:

```bash
pip install boto3 python-dotenv
```
```bash
poetry add boto3 python-dotenv
```

## Configuration

You need to set the following environment variables for the AWS credentials:

- `aws_access_key_id`
- `aws_secret_access_key`
- `aws_session_token` (Optional, should be used for AWS Labs)
- `region_name` 

You can set these variables in a `.env` file in the same directory as the script. The script uses the `dotenv` package to load these variables.

## Usage

You can use the command-line interface to interact with the S3 client. Here are the available commands:

- `--list-buckets`: List all available buckets with full body response.
- `--list-bucket-names`: List all available bucket names.
- `--delete-bucket <name>`: Delete the specified bucket.
- `--create-bucket <name>`: Create a new bucket.
- `--create-multiple-buckets <name> <first_index> <last_index>`: Create multiple buckets.
- `--delete-all-buckets`: Delete all buckets.
- `--bucket-exists <bucket_name>`: Check if the bucket exists.
- `--download-file-and-upload-to-s3 <bucket_name> <url> <file_name> <keep_local>`: Download a file and upload it to S3. Set `keep_local` to True or False.
- `--set-object-access-policy <bucket_name> <file_name>`: Set object access policy.
- `--generate-public-read-policy <bucket_name>`: Generate public read policy.
- `--create-bucket-policy <bucket_name>`: Create bucket policy.
- `--read-bucket-policy <bucket_name>`: Read bucket policy.
- `--upload-file <filename> <bucketname>`: Upload a local file to S3 Bucket.
- `--upload-file-object <filename> <bucketname>`: Upload a local file object to S3 Bucket.
- `--upload-file-put <filename> <bucketname>`: Upload a local file using the PUT method to S3 Bucket.
- `--put-lifecycle-config <bucketname>`: Apply lifecycle configuration to a bucket.
- `--multipart-upload <filename> <key> <bucketname>`: Upload a file to S3 using multipart upload.
- `--get-lifecycle-config <bucketname>`: Get the lifecycle configuration of a bucket.
- `--manage-s3-object <bucket_name> <file_name> <flag>`: Manage S3 object. The flag can be `-del`, `-copy` or `-down`.
- `--check-versioning <bucket_name>`: Check versioning status of a bucket.
- `--organize-by-type <bucket_name>`: Organize files in the bucket based on their content type.
- `--organize-by-extension <bucket_name>`: Organize files in the bucket based on their file extension.
- `--print-object-metadata <bucket_name> <object_key>`: Print metadata of an object in a bucket.

To use these commands, run the script with the desired command and its arguments. For example, to list all buckets, you would run:

```bash
python aws_s3.py --list-buckets
```

To create a new bucket named 'my-bucket', you would run:

```bash
python aws_s3.py --create-bucket my-bucket
```

And so on for the other commands.

For example, to list all available buckets, you would run:

```bash
python aws_s3.py --list-buckets
```
```bash
poetry run python aws_s3.py --list-buckets
```

## Disclaimer

Ensure that you have the required permissions to perform the operations on the S3 buckets. Use this script at your own risk.

## License

This project is open source and available under the [MIT License](LICENSE).
