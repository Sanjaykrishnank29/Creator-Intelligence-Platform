"""
Fix AWS API Gateway integrations:
- /api/chat POST -> insight_engine (chat with Bedrock)
- /api/summarize POST -> content_enhancer (trend summarization)

This script updates the integrations and redeploys the API.
"""

import boto3
import json
import time

region = "us-east-1"
api_id = "f3hmrjp4v5"
stage_name = "prod"

apigw = boto3.client("apigateway", region_name=region)
lmb = boto3.client("lambda", region_name=region)
sts = boto3.client("sts", region_name=region)

account_id = sts.get_caller_identity()["Account"]


def get_lambda_arn(fn_name):
    return f"arn:aws:lambda:{region}:{account_id}:function:{fn_name}"


def get_lambda_uri(fn_name):
    arn = get_lambda_arn(fn_name)
    return f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{arn}/invocations"


# Get all resources
resources = apigw.get_resources(restApiId=api_id, limit=100)["items"]
resource_by_path = {r["path"]: r for r in resources}
parent_id = resource_by_path.get("/api", {}).get("id") or resource_by_path.get(
    "/", {}
).get("id")

print("Current API Gateway routes:")
for r in resources:
    path = r.get("path", "")
    for method in r.get("resourceMethods", {}).keys():
        try:
            integ = apigw.get_integration(
                restApiId=api_id, resourceId=r["id"], httpMethod=method
            )
            uri = integ.get("uri", "")
            fn = (
                uri.split(":function:")[1].split("/")[0]
                if ":function:" in uri
                else uri[:60]
            )
            print(f"  {method:8} {path:35} -> {fn}")
        except:
            print(f"  {method:8} {path:35} -> (no integration)")


def ensure_resource(path):
    """Get or create an API Gateway resource for the given path."""
    if path in resource_by_path:
        return resource_by_path[path]

    # Need to create it - find parent
    parts = path.split("/")  # e.g. ['', 'api', 'chat']
    parent_path = "/".join(parts[:-1]) or "/"
    if parent_path not in resource_by_path:
        raise ValueError(f"Parent path {parent_path} not found")

    parent = resource_by_path[parent_path]
    resource = apigw.create_resource(
        restApiId=api_id, parentId=parent["id"], pathPart=parts[-1]
    )
    resource_by_path[path] = resource
    print(f"  Created resource {path}")
    return resource


def set_integration(path, method, fn_name):
    """Set or update the Lambda integration for an API Gateway route."""
    uri = get_lambda_uri(fn_name)
    resource = ensure_resource(path)
    resource_id = resource["id"]

    # Ensure method exists
    try:
        apigw.get_method(restApiId=api_id, resourceId=resource_id, httpMethod=method)
    except:
        apigw.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod=method,
            authorizationType="NONE",
        )
        print(f"  Created method {method} {path}")

    # Update integration
    apigw.put_integration(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod=method,
        type="AWS_PROXY",
        integrationHttpMethod="POST",
        uri=uri,
    )
    print(f"  Updated integration: {method} {path} -> {fn_name}")

    # Grant Lambda permission to be invoked from API Gateway
    source_arn = f"arn:aws:execute-api:{region}:{account_id}:{api_id}/*/{method}{path}"
    try:
        lmb.add_permission(
            FunctionName=fn_name,
            StatementId=f"apigateway-{path.replace('/', '-')}-{method}",
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=source_arn,
        )
        print(f"  Granted Lambda permission for {fn_name}")
    except lmb.exceptions.ResourceConflictException:
        print(f"  Lambda permission already exists for {fn_name}")
    except Exception as e:
        print(f"  Permission note: {e}")


print("\nFixing integrations...")

# Fix /api/chat -> insight_engine
set_integration("/api/chat", "POST", "creator-intelligence-dev-insight_engine")

# Fix /api/summarize -> insight_engine (create if missing)
set_integration("/api/summarize", "POST", "creator-intelligence-dev-insight_engine")

# Deploy the changes
print("\nDeploying API...")
deployment = apigw.create_deployment(
    restApiId=api_id,
    stageName=stage_name,
    description="Fix /api/chat -> insight_engine, add /api/summarize -> content_enhancer",
)
print(f"Deployment ID: {deployment['id']}")
print("Waiting for deployment to propagate...")
time.sleep(5)

print("\nVerifying updated routes:")
resources = apigw.get_resources(restApiId=api_id, limit=100)["items"]
for r in resources:
    path = r.get("path", "")
    if path in ["/api/chat", "/api/summarize"]:
        for method in r.get("resourceMethods", {}).keys():
            if method == "OPTIONS":
                continue
            try:
                integ = apigw.get_integration(
                    restApiId=api_id, resourceId=r["id"], httpMethod=method
                )
                uri = integ.get("uri", "")
                fn = (
                    uri.split(":function:")[1].split("/")[0]
                    if ":function:" in uri
                    else uri[:60]
                )
                print(f"  {method:8} {path:35} -> {fn}")
            except Exception as e:
                print(f"  {method:8} {path:35} -> ERROR: {e}")

print("\nDone! API Gateway routes updated.")
