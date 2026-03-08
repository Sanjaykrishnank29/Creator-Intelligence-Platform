import boto3
import os
import mimetypes
import json
from dotenv import load_dotenv

load_dotenv()
REGION = "us-east-1"
BUCKET = "creator-intelligence-dev-static-website"

s3 = boto3.client("s3", region_name=REGION)

print(f"Configuring {BUCKET} for static website hosting...")
s3.put_bucket_website(
    Bucket=BUCKET,
    WebsiteConfiguration={
        "ErrorDocument": {"Key": "index.html"},
        "IndexDocument": {"Suffix": "index.html"},
    },
)

print(f"Disabling Block Public Access for {BUCKET}...")
s3.delete_public_access_block(Bucket=BUCKET)

print(f"Setting public read bucket policy...")
bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": [f"arn:aws:s3:::{BUCKET}/*"],
        }
    ],
}
s3.put_bucket_policy(Bucket=BUCKET, Policy=json.dumps(bucket_policy))

print("Uploading frontend files from dist/...")
dist_dir = "dist"

for root, _, files in os.walk(dist_dir):
    for file_name in files:
        full_path = os.path.join(root, file_name)
        # S3 key should be relative to the dist directory
        s3_key = os.path.relpath(full_path, dist_dir).replace(
            "\\", "/"
        )  # Ensure forward slashes for S3

        content_type = mimetypes.guess_type(full_path)[0] or "binary/octet-stream"
        print(f" -> Uploading {s3_key} ({content_type})...")

        s3.upload_file(
            Filename=full_path,
            Bucket=BUCKET,
            Key=s3_key,
            ExtraArgs={"ContentType": content_type},
        )

print("\n==========================================")
print("✅ Frontend Deployed Successfully!")
print(f"Live Website URL: http://{BUCKET}.s3-website-{REGION}.amazonaws.com")
print("==========================================")
