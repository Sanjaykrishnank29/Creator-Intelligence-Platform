import boto3
import os
import mimetypes
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.getenv("Access_key")
SECRET_KEY = os.getenv("Secret_access_key")
REGION = "us-east-1"
PROJECT = "creator-intelligence"
ENV = "dev"
BUCKET = f"{PROJECT}-{ENV}-static-website"


def get_client(service):
    return boto3.client(
        service,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION,
    )


def upload_frontend():
    s3 = get_client("s3")
    dist_dir = os.path.abspath("dist")

    if not os.path.exists(dist_dir):
        print("❌ dist folder not found. Build the project first.")
        return

    print(f"Uploading frontend to s3://{BUCKET}...")
    for root, _, files in os.walk(dist_dir):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, dist_dir).replace("\\", "/")

            content_type, _ = mimetypes.guess_type(full_path)
            if content_type is None:
                content_type = "application/octet-stream"

            print(f"  Uploading {rel_path} ({content_type})...")
            s3.upload_file(
                full_path, BUCKET, rel_path, ExtraArgs={"ContentType": content_type}
            )

    print("✅ Frontend upload complete.")

    # Configure for Static Website Hosting
    print("Configuring S3 for static website hosting...")
    s3.put_bucket_website(
        Bucket=BUCKET,
        WebsiteConfiguration={
            "ErrorDocument": {"Key": "index.html"},
            "IndexDocument": {"Suffix": "index.html"},
        },
    )

    # Open Public Access (For Demo)
    print("Setting public bucket policy...")
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{BUCKET}/*",
            }
        ],
    }

    # Remove block public access first
    s3.put_public_access_block(
        Bucket=BUCKET,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": False,
            "IgnorePublicAcls": False,
            "BlockPublicPolicy": False,
            "RestrictPublicBuckets": False,
        },
    )

    s3.put_bucket_policy(Bucket=BUCKET, Policy=json.dumps(policy))

    print(f"🚀 Live URL: http://{BUCKET}.s3-website-{REGION}.amazonaws.com")


if __name__ == "__main__":
    import json

    upload_frontend()
