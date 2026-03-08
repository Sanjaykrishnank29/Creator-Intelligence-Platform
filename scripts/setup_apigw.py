import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.getenv("Access_key")
SECRET_KEY = os.getenv("Secret_access_key")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
PROJECT = "creator-intelligence"
ENV = "dev"


def get_client(service):
    return boto3.client(
        service,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION,
    )


def get_account_id():
    sts = get_client("sts")
    return sts.get_caller_identity()["Account"]


def add_cors(apigw, api_id, resource_id):
    # Add OPTIONS method for CORS preflight
    apigw.put_method(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod="OPTIONS",
        authorizationType="NONE",
    )
    apigw.put_integration(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod="OPTIONS",
        type="MOCK",
        requestTemplates={"application/json": '{"statusCode": 200}'},
    )
    apigw.put_method_response(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod="OPTIONS",
        statusCode="200",
        responseParameters={
            "method.response.header.Access-Control-Allow-Headers": True,
            "method.response.header.Access-Control-Allow-Methods": True,
            "method.response.header.Access-Control-Allow-Origin": True,
        },
    )
    apigw.put_integration_response(
        restApiId=api_id,
        resourceId=resource_id,
        httpMethod="OPTIONS",
        statusCode="200",
        responseParameters={
            "method.response.header.Access-Control-Allow-Headers": "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
            "method.response.header.Access-Control-Allow-Methods": "'GET,OPTIONS,POST,PUT,DELETE'",
            "method.response.header.Access-Control-Allow-Origin": "'*'",
        },
    )


def setup_apigw():
    apigw = get_client("apigateway")
    l_client = get_client("lambda")

    api_name = f"{PROJECT}-{ENV}-api"
    account_id = get_account_id()

    # Check if API exists
    api_id = None
    apis = apigw.get_rest_apis()["items"]
    for a in apis:
        if a["name"] == api_name:
            api_id = a["id"]
            break

    if not api_id:
        print(f"Creating REST API {api_name}...")
        api = apigw.create_rest_api(
            name=api_name,
            description="Creator Intelligence Platform API",
            endpointConfiguration={"types": ["REGIONAL"]},
        )
        api_id = api["id"]

    print(f"✅ Using API ID: {api_id}")

    resources = apigw.get_resources(restApiId=api_id)["items"]
    root_id = [r["id"] for r in resources if r["path"] == "/"][0]

    # Create /api
    api_res_id = None
    for r in resources:
        if r["path"] == "/api":
            api_res_id = r["id"]
            break
    if not api_res_id:
        api_res = apigw.create_resource(
            restApiId=api_id, parentId=root_id, pathPart="api"
        )
        api_res_id = api_res["id"]

    endpoints = [
        {"path": "posts", "method": "GET", "lambda": "content_ingestion"},
        {"path": "profile", "method": "GET", "lambda": "insight_engine"},
        {"path": "predict", "method": "POST", "lambda": "prediction_api"},
        {"path": "analyze", "method": "POST", "lambda": "insight_engine"},
        {"path": "summarize", "method": "POST", "lambda": "insight_engine"},
        {"path": "generate", "method": "POST", "lambda": "idea_generator"},
        {"path": "chat", "method": "POST", "lambda": "idea_generator"},
    ]

    for ep in endpoints:
        path = ep["path"]
        method = ep["method"]
        fn_name = f"{PROJECT}-{ENV}-{ep['lambda']}"
        lambda_arn = f"arn:aws:lambda:{REGION}:{account_id}:function:{fn_name}"

        # Create resource
        res_id = None
        for r in resources:
            if r["path"] == f"/api/{path}":
                res_id = r["id"]
                break
        if not res_id:
            print(f"Creating /api/{path}...")
            res = apigw.create_resource(
                restApiId=api_id, parentId=api_res_id, pathPart=path
            )
            res_id = res["id"]
            # Re-fetch resources to include new ones in next loops
            resources = apigw.get_resources(restApiId=api_id)["items"]

        # Add CORS
        try:
            add_cors(apigw, api_id, res_id)
        except Exception as e:
            print(f"ℹ️ CORS setup for {path} note: {e}")

        # Add Method
        print(f"Setting up {method} /api/{path} -> {fn_name}")
        try:
            apigw.put_method(
                restApiId=api_id,
                resourceId=res_id,
                httpMethod=method,
                authorizationType="NONE",
            )
        except apigw.exceptions.ConflictException:
            pass
        except Exception as e:
            print(f"Method error: {e}")

        try:
            apigw.put_integration(
                restApiId=api_id,
                resourceId=res_id,
                httpMethod=method,
                type="AWS_PROXY",
                integrationHttpMethod="POST",
                uri=f"arn:aws:apigateway:{REGION}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations",
            )
        except Exception as e:
            print(f"Integration error: {e}")

        # Permissions
        try:
            l_client.add_permission(
                FunctionName=fn_name,
                StatementId=f"apigw-{api_id}-{path}",
                Action="lambda:InvokeFunction",
                Principal="apigateway.amazonaws.com",
                SourceArn=f"arn:aws:execute-api:{REGION}:{account_id}:{api_id}/*",
            )
        except Exception:
            pass

    # Deploy
    print("Deploying API stage 'prod'...")
    apigw.create_deployment(restApiId=api_id, stageName="prod")
    print(
        f"🚀 Live API URL: https://{api_id}.execute-api.{REGION}.amazonaws.com/prod/api"
    )


if __name__ == "__main__":
    setup_apigw()
