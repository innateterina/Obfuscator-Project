def parse_s3_location(s3_location: str):
    path_part = s3_location.replace('s3://', '').split('/')
    bucket_name = path_part[0]
    file_key = '/'.join(path_part[1:])
    return bucket_name, file_key


def replace_pii_data(row: dict, pii_fields: list):
    for field in pii_fields:
        if field in row:
            row[field] = '***'
    return row

