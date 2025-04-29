def generate_bucket_name(*, account_id: str, region: str) -> str:
    return f"artifact-bucket-{account_id}-{region}"
