# AWS S3 Client

This project is a simple AWS S3 client that can be used to interact with S3 buckets. It allows you to list, create, delete, and upload files to S3 buckets. It also includes a command-line interface for easy interaction.

## Features

- List all available S3 buckets
- Create new S3 buckets
- Delete existing S3 buckets
- Upload files to S3 buckets
- Download files from a URL and upload them to S3
- Set object access policies
- Generate public read policies for buckets
- Create bucket policies
- Read bucket policies

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

- `--list-buckets`: List all available buckets
- `--list-bucket-names`: List all available bucket names
- `--delete-bucket`: Delete the specified bucket
- `--create-bucket`: Create a new bucket
- `--create-multiple-buckets`: Create multiple buckets
- `--delete-all-buckets`: Delete all buckets
- `--bucket-exists`: Check if the bucket exists
- `--download-file-and-upload-to-s3`: Download a file and upload it to S3
- `--set-object-access-policy`: Set object access policy
- `--generate-public-read-policy`: Generate public read policy
- `--create-bucket-policy`: Create bucket policy
- `--read-bucket-policy`: Read bucket policy

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
