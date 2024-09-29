import json
from main.main import obfuscate_upload


def lambda_handler(event, context):
    """
    AWS Lambda  entry point.
    Invoked by EventBridge when triggered by an event.
    Expected input format in event for example:
    {
    "input_s3_location":
    "s3://input_bucket/input_file.csv",
    "output_s3_location":
    "s3://output_bucket/output_file.csv",
    "pii_fields": ["name", "email"]
    }
    """
    input_s3_location = event.get("input_s3_location")
    output_s3_location = event.get("output_s3_location")
    pii_fields = event.get("pii_fields", [])

    try:
        obfuscate_upload(input_s3_location, output_s3_location, pii_fields)
        return {
            "statusCode": 200,
            "body": json.dumps("Obfuscation process completed successfully."),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error during obfuscation process: {str(e)}"),
        }
