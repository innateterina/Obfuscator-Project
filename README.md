# GDPR Obfuscator Project

## Project Overview

The purpose of this project is to create a tool to obfuscate personally identifiable information (PII) in data stored in AWS S3. This tool ensures that sensitive data is anonymized to comply with GDPR regulations, making the information safe for bulk analysis.

## Features

- Obfuscates PII in CSV, JSON, and Parquet files stored in S3.
- Supports obfuscation of specified fields while keeping primary key fields intact.
- Can be invoked as a library module or through an AWS Lambda function.

## Project Structure

- **`main/`**: Core project folder containing the main code and helper functions.
  - `helpers.py`: Utility functions for parsing S3 locations, replacing PII, and uploading results.
  - `main.py`: Functions for obfuscating CSV, JSON, and Parquet files from S3.
  - `obfuscate_cli.py`: Command-line interface to test the obfuscation locally.
  - `lambda_function.py`: Lambda handler for AWS invocation.
- **`lambda_layer/`**: AWS Lambda Layers containing `numpy`, `pyarrow`, `pandas` for use in the Lambda function.
- **`scripts/`**: Scripts for setup automation.
  - `setup_eventbridge.sh`: Script to create an EventBridge rule to trigger the Lambda function.
- **`test/`**: Unit tests for different components of the project.
- **`venv/`**: Python virtual environment (should be ignored in `.gitignore`).

## Setup Instructions

### Step 1: Install Dependencies

Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Prepare Lambda Layers

To use numpy, pyarrow, and pandas in AWS Lambda, prepare the Lambda layers:

```bash
mkdir -p lambda_layer/python
pip install numpy pyarrow pandas -t lambda_layer/python
cd lambda_layer
zip -r data_layer.zip python
```

### Step 3: Create Deployment Package

Create the deployment package for the Lambda function:

```bash
zip -r deployment_package.zip main/ requirements.txt

```

### Step 4: Setup AWS Lambda and EventBridge

Edit scripts/setup_eventbridge.sh to set your AWS region, account ID, and role ARN. Then run the script:

```bash
chmod +x scripts/setup_eventbridge.sh
./scripts/setup_eventbridge.sh

```

### Step 5: Run Locally (CLI)

To test the obfuscation locally using the command-line interface:

```bash
python main/obfuscate_cli.py --input_file_path "main/input.csv" --output_file_path "main/output.csv" --pii_fields name email

```

```bash
python main/obfuscate_cli.py --input_file_path "main/input.json" --output_file_path "main/output.json" --pii_fields name email age id
```

### Running Tests

Run tests to verify the functionality:

```bash
python -m unittest discover -s test
```

### Check Code Compliance

To check for PEP-8 compliance:

```bash
flake8 --exclude='*.zip,venv,lambda_layer,.coverage'
```

### Example Input and Output

Example JSON Input:

[{"id": 1, "name": "John Ford", "email": "john@example.com", "age": 25},
{"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 30}]

Example Output (Obfuscated name, email, age and id fields, and id field is actually not obfuscated because it's a primary key):

[{"id": 1, "name": "***", "email": "***", "age": "***"}, {"id": 2, "name": "***", "email": "***", "age": "***"}]

### Summary

This project provides a Python library to obfuscate PII in CSV, JSON, and Parquet files.
It can be deployed as an AWS Lambda function and triggered by EventBridge.
All sensitive fields (except those with 'id' in the name) are obfuscated.
Easily testable through CLI or AWS Lambda integration.
