import boto3


def parse_s3_location(s3_location: str):
    """
    Function parses s3 URI into bucket name and file key.
    """
    path_part = s3_location.replace("s3://", "").split("/")
    bucket_name = path_part[0]
    file_key = "/".join(path_part[1:])
    return bucket_name, file_key


def replace_pii_csv_data(row: dict, pii_fields: list):
    """
    Function obfuscates sensitive pii fields in a csv row,
    excluding the primary key (assumed to be the first column).
    """
    primary_key = list(row.keys())[0]

    for field in pii_fields:
        if field in row and field != primary_key:
            row[field] = "***"
    return row


def replace_pii_json_data(data: dict, pii_fields: list, is_top_level=True):
    """
    Function obfuscates pii fields in JSON data recursively,
    excluding the primary key (assumed to be the first key).
    """
    if isinstance(data, dict):
        primary_key = next(iter(data)) if is_top_level else None
        for key, value in data.items():
            if key in pii_fields and isinstance(value, str):
                if not is_top_level or key != primary_key:
                    data[key] = "***"
            elif isinstance(value, (dict, list)):
                replace_pii_json_data(value, pii_fields, is_top_level=False)
    elif isinstance(data, list):
        for item in data:
            replace_pii_json_data(item, pii_fields, is_top_level=False)


def upload_obfuscated_file(bucket_name: str, file_key=str, data=bytes):
    """
    Function uploads obfuscated file to the specified s3 location.
    """
    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket_name, Key=file_key, Body=data)
    print(f"File uploaded to s3://{bucket_name}/{file_key}")
