"""
Deploy AI Lambda functions — Nova Lite standardized.
"""

import boto3
import zipfile
import io
import os
import time

region = "us-east-1"
lmb = boto3.client("lambda", region_name=region)

LAMBDAS = [
    ("creator-intelligence-dev-insight_engine", "lambdas/insight_engine"),
    ("creator-intelligence-dev-idea_generator", "lambdas/idea_generator"),
    ("creator-intelligence-dev-content_enhancer", "lambdas/content_enhancer"),
]


def zip_lambda(folder):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in files:
                if f.endswith(".pyc"):
                    continue
                full = os.path.join(root, f)
                arcname = os.path.relpath(full, folder)
                z.write(full, arcname)
    return buf.getvalue()


print("Deploying Lambda functions (Nova Lite only)...\n")

results = []
for fn_name, folder in LAMBDAS:
    short = fn_name.replace("creator-intelligence-dev-", "")
    try:
        zip_bytes = zip_lambda(folder)
        print(f"[{short}] Uploading {len(zip_bytes) // 1024} KB...")
        resp = lmb.update_function_code(FunctionName=fn_name, ZipFile=zip_bytes)
        code_size = resp.get("CodeSize", 0)
        print(f"[{short}] Upload OK | CodeSize={code_size // 1024} KB")
        results.append((short, True))
    except Exception as e:
        print(f"[{short}] FAILED: {e}")
        results.append((short, False))

print("\nWaiting 10s for Lambda to stabilize...")
time.sleep(10)

print("\nFinal status:")
for fn_name, _ in LAMBDAS:
    short = fn_name.replace("creator-intelligence-dev-", "")
    try:
        c = lmb.get_function_configuration(FunctionName=fn_name)
        s = c.get("LastUpdateStatus", "Unknown")
        m = c["MemorySize"]
        t = c["Timeout"]
        icon = "✅" if s in ("Successful", "InProgress") else "❌"
        print(f"  {icon} {short}: status={s} memory={m}MB timeout={t}s")
    except Exception as e:
        print(f"  ❌ {short}: {e}")
