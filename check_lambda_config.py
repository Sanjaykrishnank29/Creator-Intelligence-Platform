import boto3

lmb = boto3.client("lambda", region_name="us-east-1")
fns = [
    "creator-intelligence-dev-insight_engine",
    "creator-intelligence-dev-content_enhancer",
    "creator-intelligence-dev-idea_generator",
]
for fn in fns:
    c = lmb.get_function_configuration(FunctionName=fn)
    short = fn.split("dev-")[1]
    mem = c["MemorySize"]
    timeout = c["Timeout"]
    runtime = c["Runtime"]
    env = c.get("Environment", {}).get("Variables", {})
    model = env.get("BEDROCK_MODEL_ID", env.get("MODEL_ID", "(not set)"))
    print(f"{short}: Memory={mem}MB Timeout={timeout}s Runtime={runtime}")
    print(f"  Model env var: {model}")
    print(f"  All env keys: {list(env.keys())}")
    print()
