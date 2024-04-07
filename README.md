# AWS S3 Client

This S3 Client provides a variety of features for managing AWS S3 buckets and objects. While the current functionality includes operations such as listing, creating, and deleting buckets, as well as uploading files and managing access policies, you might see more features added to enhance the tool's capabilities.

## Installation

Before running the script, make sure to install the required packages. You can install them using pip or poetry:

```bash
pip install -r requirements.txt
```
```bash
poetry install
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

# AWS S3 CLI Commands

- `--list-buckets`: List all available buckets (Full Body Response).
- `--list-bucket-names`: List all available bucket names.
- `--delete-bucket`: Delete the specified bucket. Argument: `name`.
- `--create-bucket`: Create a new bucket. Argument: `name`.
- `--create-multiple-buckets`: Create multiple buckets. Arguments: `name`, `first_index`, `last_index`.
- `--delete-all-buckets`: Delete all buckets.
- `--bucket-exists`: Check if the bucket exists. Argument: `bucket_name`.
- `--download-file-and-upload-to-s3`: Download a file and upload it to S3. Arguments: `bucket_name`, `url`, `file_name`, `keep_local`.
- `--set-object-access-policy`: Set object access policy. Arguments: `bucket_name`, `file_name`.
- `--generate-public-read-policy`: Generate public read policy. Argument: `bucket_name`.
- `--create-bucket-policy`: Create bucket policy. Argument: `bucket_name`.
- `--read-bucket-policy`: Read bucket policy. Argument: `bucket_name`.
- `--upload-file`: Upload a local file to S3 Bucket. Arguments: `bucketname`, `filename`.
- `--upload-file-object`: Upload a local file object to S3 Bucket. Arguments: `bucketname`, `filename`.
- `--upload-file-put`: Upload a local file using the PUT method to S3 Bucket. Arguments: `bucketname`, `filename`.
- `--put-lifecycle-config`: Apply lifecycle configuration to a bucket. Argument: `bucketname`.
- `--multipart-upload`: Upload a file to S3 using multipart upload. Arguments: `bucketname`, `key`, `filename`.
- `--get-lifecycle-config`: Get the lifecycle configuration of a bucket. Argument: `bucketname`.
- `--manage-s3-object`: Manage S3 object. Arguments: `bucket_name`, `file_name`, `flag`. The `flag` argument can take the following values:
  - `-del`: Delete the specified S3 object.
  - `-copy`: Copy the specified S3 object.
  - `-down`: Download the specified S3 object.
- `--check-versioning`: Check versioning status of a bucket. Argument: `bucket_name`.
- `--organize-by-type`: Organize files in the bucket based on their content type. Argument: `bucket_name`.
- `--organize-by-extension`: Organize files in the bucket based on their extension. Argument: `bucket_name`.
- `--print-object-metadata`: Print metadata of an object in a bucket. Arguments: `bucket_name`, `object_key`.
- `--upload-file-to-folder`: Upload a file to a folder in S3 Bucket. Arguments: `bucketname`, `filename`.
- `--rollback-to-first`: Rolls back the object in the S3 Bucket to its first version. Arguments: `bucket_name`, `object_key`
- `--clean-old-versions`: Clean old versions of a file in a bucket. Arguments: `bucket_name`, `filename`, `day`.
- `--configure-website`: Configure website for a bucket. Arguments: `bucket_name`, `flag`. The `flag` argument can take the following values:
  - `get`: Get the website configuration for the specified bucket.
  - `set`: Set the website configuration for the specified bucket.
  - `upload`: Upload the website configuration to the specified bucket.
  - `delete`: Delete the website configuration from the specified bucket.
- `--inspire`: Generate and display or upload a random quote to S3 bucket from the specified author. Arguments: `author`, `flag (save or show)`.
- `--create-website`: Create a website in an S3 bucket from a website source directory (Usually includes css, javascript, image files and folders) (Arguments: bucket_name, sourcedir)

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
