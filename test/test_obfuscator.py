import unittest
from unittest.mock import patch
from main.helpers import (
    parse_s3_location,
    replace_pii_csv_data,
    replace_pii_json_data,
    upload_obfuscated_file,
)
from main.main import (obfuscate_upload,
                       obfuscate_json, obfuscate_csv, obfuscate_parquet)
from io import BytesIO
import pandas as pd
import json


class TestObfuscator(unittest.TestCase):

    # Test for parse_s3_location()
    def test_parse_s3_location(self):
        s3_location = "s3://my_bucket/my_folder/my_file.csv"
        bucket, key = parse_s3_location(s3_location)
        self.assertEqual(bucket, "my_bucket")
        self.assertEqual(key, "my_folder/my_file.csv")

    # Test for replace_pii_csv_data()
    def test_replace_pii_csv_data(self):
        row = {"name": "John Ford", "email": "john@example.com", "age": "30"}
        pii_fields = ["name", "email"]
        obfuscated_row = replace_pii_csv_data(row, pii_fields)
        self.assertEqual(obfuscated_row["name"], "***")
        self.assertEqual(obfuscated_row["email"], "***")
        self.assertEqual(obfuscated_row["age"], "30")

    # Test for replace_pii_json_data()
    def test_replace_pii_json_data(self):
        data = {
            "name": "Jane Ford",
            "email": "jane@example.com",
            "details": {"phone": "1234567890", "address": "123 Main St"},
        }
        pii_fields = ["name", "email", "phone"]
        replace_pii_json_data(data, pii_fields)
        self.assertEqual(data["name"], "***")
        self.assertEqual(data["email"], "***")
        self.assertEqual(data["details"]["phone"], "***")
        self.assertEqual(data["details"]["address"], "123 Main St")

    # Test for upload_obfuscated_file()
    @patch("boto3.client")
    def test_upload_obfuscated_file(self, mock_boto):
        # Mock the S3 client and put_object
        s3_mock = mock_boto.return_value
        upload_obfuscated_file("my_bucket", "my_file.csv", b"obfuscated data")
        s3_mock.put_object.assert_called_once_with(
            Bucket="my_bucket", Key="my_file.csv", Body=b"obfuscated data"
        )

    # Test for obfuscate_json()
    @patch("boto3.client")
    def test_obfuscate_json(self, mock_boto):
        s3_mock = mock_boto.return_value
        mock_s3_response = {
            "Body": BytesIO(
                json.dumps(
                    {"name": "Jane Ford",
                     "email": "jane@example.com",
                     "age": 30}
                ).encode("utf-8")
            )
        }
        s3_mock.get_object.return_value = mock_s3_response

        pii_fields = ["name", "email"]
        result = obfuscate_json("s3://my_bucket/my_file.json", pii_fields)
        expected_output = json.dumps({"name": "***",
                                      "email": "***",
                                      "age": 30}
                                     ).encode("utf-8"
                                              )

        self.assertEqual(result, expected_output)

    # Test for obfuscate_csv()
    @patch("boto3.client")
    def test_obfuscate_csv(self, mock_boto):
        s3_mock = mock_boto.return_value
        mock_s3_response = {
            "Body": BytesIO(
                "name,email,"
                "age\nJane Ford,"
                "jane@example.com,"
                "30\nJohn Smith,john@example.com,25".encode(
                    "utf-8"
                )
            )
        }
        s3_mock.get_object.return_value = mock_s3_response

        pii_fields = ["name", "email"]
        result = obfuscate_csv("s3://my_bucket/my_file.csv", pii_fields)
        result = result.replace(b"\r\n", b"\n")
        expected_output = "name,email,age\n***,***,30\n***,***,25\n".encode(
            "utf-8")

        self.assertEqual(result, expected_output)

    # Test for obfuscate_parquet()
    @patch("boto3.client")
    def test_obfuscate_parquet(self, mock_boto):
        s3_mock = mock_boto.return_value
        df = pd.DataFrame(
            {
                "name": ["Jane Ford", "John Smith"],
                "email": ["jane@example.com", "john@example.com"],
                "age": [30, 25],
            }
        )
        parquet_file = BytesIO()
        df.to_parquet(parquet_file, index=False)
        parquet_file.seek(0)

        mock_s3_response = {"Body": parquet_file}
        s3_mock.get_object.return_value = mock_s3_response

        pii_fields = ["name", "email"]
        result = obfuscate_parquet(
            "s3://my_bucket/my_file.parquet", pii_fields)

        # Convert result back to dataframe for assertion
        result_df = pd.read_parquet(BytesIO(result))
        expected_df = pd.DataFrame(
            {"name": ["***", "***"], "email": ["***", "***"], "age": [30, 25]}
        )

        pd.testing.assert_frame_equal(result_df, expected_df)

    # Test for obfuscate_upload()
    @patch("main.main.upload_obfuscated_file")
    @patch("main.main.obfuscate_parquet")
    @patch("main.main.obfuscate_csv")
    @patch("main.main.obfuscate_json")
    def test_obfuscate_upload(
        self,
        mock_obfuscate_json,
        mock_obfuscate_csv,
        mock_obfuscate_parquet,
        mock_upload,
    ):
        # Mocking the individual obfuscate functions
        mock_obfuscate_json.return_value = b"obfuscated json data"
        mock_obfuscate_csv.return_value = b"obfuscated csv data"
        mock_obfuscate_parquet.return_value = b"obfuscated parquet data"

        # Test JSON obfuscation
        obfuscate_upload(
            "s3://my_bucket/my_file.json",
            "s3://my_bucket/obfuscated_file.json",
            ["name", "email"],
        )
        mock_obfuscate_json.assert_called_once()
        mock_upload.assert_called_once_with(
            "my_bucket", "obfuscated_file.json", b"obfuscated json data"
        )

        # Reset mocks
        mock_obfuscate_json.reset_mock()
        mock_upload.reset_mock()

        # Test CSV obfuscation
        obfuscate_upload(
            "s3://my_bucket/my_file.csv",
            "s3://my_bucket/obfuscated_file.csv",
            ["name", "email"],
        )
        mock_obfuscate_csv.assert_called_once()
        mock_upload.assert_called_once_with(
            "my_bucket", "obfuscated_file.csv", b"obfuscated csv data"
        )

        # Reset mocks
        mock_obfuscate_csv.reset_mock()
        mock_upload.reset_mock()

        # Test Parquet obfuscation
        obfuscate_upload(
            "s3://my_bucket/my_file.parquet",
            "s3://my_bucket/obfuscated_file.parquet",
            ["name", "email"],
        )
        mock_obfuscate_parquet.assert_called_once()
        mock_upload.assert_called_once_with(
            "my_bucket", "obfuscated_file.parquet", b"obfuscated parquet data"
        )
