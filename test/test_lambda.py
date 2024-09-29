import unittest
from unittest.mock import patch
import json
from main.lambda_function import lambda_handler


class TestLambdaFunction(unittest.TestCase):

    @patch("main.lambda_function.obfuscate_upload")
    @patch("boto3.client")
    def test_lambda_handler_success(self, mock_boto, mock_obfuscate_upload):
        # Arrange
        event = {
            "input_s3_location": "s3://input_bucket/input_file.csv",
            "output_s3_location": "s3://output_bucket/output_file.csv",
            "pii_fields": ["name", "email"],
        }
        context = {}  # AWS Lambda context (not used in this test)

        # Mock obfuscate_upload to simulate successful obfuscation
        mock_obfuscate_upload.return_value = None

        # Act
        response = lambda_handler(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(json.loads(response["body"]),
                         "Obfuscation process "
                         "completed successfully."
                         )
        mock_obfuscate_upload.assert_called_once_with(
            event["input_s3_location"],
            event["output_s3_location"],
            event["pii_fields"]
        )

    @patch("main.lambda_function.obfuscate_upload")
    @patch("boto3.client")
    def test_lambda_handler_failure(self, mock_boto, mock_obfuscate_upload):
        # Arrange
        event = {
            "input_s3_location": "s3://input_bucket/input_file.csv",
            "output_s3_location": "s3://output_bucket/output_file.csv",
            "pii_fields": ["name", "email"],
        }
        context = {}

        # Mock obfuscate_upload to simulate an exception being raised
        mock_obfuscate_upload.side_effect = Exception("Test Exception")

        # Act
        response = lambda_handler(event, context)

        # Assert
        self.assertEqual(response["statusCode"], 500)
        self.assertIn("Error during obfuscation process",
                      json.loads(response["body"]))
