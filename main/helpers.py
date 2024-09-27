def parse_s3_location(s3_location: str):
    path_part = s3_location.replace('s3://', '').split('/')
    bucket_name = path_part[0]
    file_key = '/'.join(path_part[1:])
    return bucket_name, file_key


def replace_pii_csv_data(row: dict, pii_fields: list):
    for field in pii_fields:
        if field in row:
            row[field] = '***'
    return row


def replace_pii_json_data(data: dict, pii_fields: list):
    if isinstance(data, dict):
        for key, value in data.items():
            if key in pii_fields and isinstance(value, str):
                data[key] = '***'
            elif isinstance(value, (dict, list)):
                replace_pii_json_data(value, pii_fields)
    elif isinstance(data, list):
        for item in data:
            replace_pii_json_data(item, pii_fields)


def upload_obfuscated_file(bucket_name: str, file_key=str, data=bytes):
    s3 = boto3.client('s3')
    s3.put_object(Bucket=bucket_name, Key=file_key, Body=data)
    print(f"File uploaded to s3://{bucket_name}/{file_key}")
