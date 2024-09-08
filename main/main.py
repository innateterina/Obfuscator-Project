# the S3 location of the required CSV file for obfuscation
# the names of the fields that are required to be obfuscated
# For example, the input might be:

# {
#     "file_to_obfuscate": "s3://my_ingestion_bucket/new_data/file1.csv",
#     "pii_fields": ["name", "email_address"]
# }
# The target CSV file might look like this:

# student_id,name,course,cohort,graduation_date,email_address
# ...
# 1234,'John Smith','Software','2024-03-31','j.smith@email.com'
# ...
# The output will be a byte-stream representation of a file like this:

# student_id,name,course,cohort,graduation_date,email_address
# ...
# 1234,'***','Software','2024-03-31','***'
import boto3
import csv
from io import StringIO
from helpers import parse_s3_location, replace_pii_data


def obfusc_csv(s3_location: str,  pii_fields: list):
    s3 = boto3.client('s3')
    bucket_name, file_key = parse_s3_location(s3_location)
    obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    data = obj['Body'].read().decode('utf-8')
    csv_input = StringIO(data)
    csv_output = StringIO()

    reader = csv.DictReader(csv_input)
    writer = csv.DictWriter(csv_output, fieldnames=reader.fieldnames)
    writer.writeheader()
    for row in reader:
        obfusc_row = replace_pii_data(row, pii_fields)
        writer.writerow(obfusc_row)
    return csv_output.getvalue().encode('utf-8')


input_json = {
    "file_to_obfuscate": "s3://my_ingestion_bucket/new_data/file1.csv",
    "pii_fields": ["name", "email_address"]
}

obfusc_data = obfusc_csv(
    input_json['file_to_obfuscate'], input_json['pii_fields'])
