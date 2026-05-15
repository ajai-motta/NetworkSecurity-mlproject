import os



def sync_s3_bucket(bucket_name: str, local_directory: str) -> None:
    """
    Sync a local directory with an S3 bucket.

    Args:
        bucket_name (str): The name of the S3 bucket.
        local_directory (str): The path to the local directory to sync.

    Returns:
        None
    """
    try:
        command = f"aws s3 sync {local_directory} s3://{bucket_name}"
        os.system(command)
        print(f"Successfully synced {local_directory} with s3://{bucket_name}")
    except Exception as e:
        print(f"Error syncing with S3 bucket: {str(e)}")