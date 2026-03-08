"""Deploy only the content_ingestion Lambda."""

import boto3
import zipfile
import io
import os
import time

region = "us-east-1"
lmb = boto3.client("lambda", region_name=region)

fn_name = "creator-intelligence-dev-content_ingestion"
folder = "lambdas/content_ingestion"


def zip_lambda(fldr):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(fldr):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in files:
                if f.endswith(".pyc"):
                    continue
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, fldr))
    return buf.getvalue()


from dotenv import load_dotenv

load_dotenv(override=True)

print(f"Deploying {fn_name}...")
zip_bytes = zip_lambda(folder)
try:
    lmb.update_function_code(FunctionName=fn_name, ZipFile=zip_bytes)

    print("Waiting for code update to complete...")
    while True:
        c = lmb.get_function_configuration(FunctionName=fn_name)
        if c.get("LastUpdateStatus") == "Successful":
            break
        time.sleep(2)

    # Update environment variables
    lmb.update_function_configuration(
        FunctionName=fn_name,
        Environment={
            "Variables": {
                "CONTENT_TABLE": os.getenv(
                    "CONTENT_TABLE", "creator-intelligence-dev-CreatorContent"
                ),
                "DATASET_BUCKET": os.getenv(
                    "DATASET_BUCKET", "creator-intelligence-dev-datasets"
                ),
                "YOUTUBE_API_KEY": os.getenv("YOUTUBE_API_KEY", ""),
                "YOUTUBE_CHANNEL_ID": os.getenv("YOUTUBE_CHANNEL_ID", ""),
            }
        },
    )

    print("✅ Upload complete. Stabilizing...")
    time.sleep(5)
    c = lmb.get_function_configuration(FunctionName=fn_name)
    print(f"✅ Status: {c.get('LastUpdateStatus', 'Unknown')}")
except Exception as e:
    print(f"❌ Failed: {e}")
