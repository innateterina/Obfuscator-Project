import time
from helpers import (
    replace_pii_csv_data,
    replace_pii_json_data
)
import argparse
import json
import csv
from io import StringIO


def obfuscate_upload(input_file_path: str,
                     output_file_path: str,
                     pii_fields: list):
    """
    Reads a local file, obfuscates the PII fields,
    and saves it back to a new location.
    """
    if input_file_path.endswith(".csv"):
        result = obfuscate_csv(input_file_path, pii_fields)
    elif input_file_path.endswith(".json"):
        result = obfuscate_json(input_file_path, pii_fields)
    else:
        raise ValueError(
            "Unsupported file format.")

    # Save obfuscated result
    with open(output_file_path, 'w') as f:
        f.write(result)
    print(f"File successfully obfuscated and saved to {output_file_path}")


def obfuscate_csv(file_path: str, pii_fields: list):
    """
    Reads a CSV file, obfuscates specified PII fields,
    and returns the obfuscated CSV content.
    """
    with open(file_path, newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=reader.fieldnames)
        writer.writeheader()

        for row in reader:
            obfuscated_row = replace_pii_csv_data(row, pii_fields)
            writer.writerow(obfuscated_row)

    return output.getvalue()


def obfuscate_json(file_path: str, pii_fields: list):
    """
    Reads a JSON file, obfuscates specified PII fields,
    and returns the obfuscated JSON content.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)

    replace_pii_json_data(data, pii_fields)

    return json.dumps(data)


start_time = time.time()
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Obfuscate PII in files')
    parser.add_argument('--input_file_path', type=str,
                        required=True, help='Input file path (local)')
    parser.add_argument('--output_file_path', type=str,
                        required=True, help='Output file path (local)')
    parser.add_argument('--pii_fields', type=str, nargs='+',
                        required=True, help='List of PII fields')

    args = parser.parse_args()

    obfuscate_upload(
        args.input_file_path,
        args.output_file_path,
        args.pii_fields,
    )
# python main/obfuscate_cli.py --input_file_path "main/input.csv"
# --output_file_path "main/output.csv"
# --pii_fields name email


# python main/obfuscate_cli.py --input_file_path "main/input.json"
# --output_file_path "main/output.json"
# --pii_fields name email age id

end_time = time.time()
print(f"Runtime: {end_time - start_time} seconds")
