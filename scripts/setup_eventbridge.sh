#!/bin/bash

# Set variables
RULE_NAME="MyScheduledRule"
FUNCTION_NAME="MyLambdaFunction"
STATEMENT_ID="MyStatementId"
REGION="your-region"  
ACCOUNT_ID="your-account-id"  # Your AWS account ID
SCHEDULE_EXPRESSION="rate(5 minutes)"
TARGET_ID="1"
ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/execution_role"  # Replace with your actual role ARN

# Step 1: Create the Lambda function
echo "Creating Lambda function: $FUNCTION_NAME"
aws lambda create-function \
  --function-name "$FUNCTION_NAME" \
  --zip-file fileb://deployment_package.zip \
  --handler main.lambda_handler \
  --runtime python3.8 \
  --role "$ROLE_ARN" \
  --region "$REGION"

# Step 2: Create EventBridge rule
echo "Creating EventBridge rule: $RULE_NAME"
aws events put-rule --name "$RULE_NAME" --schedule-expression "$SCHEDULE_EXPRESSION" --region "$REGION"

# Step 3: Add permission to Lambda function for EventBridge to invoke it
echo "Adding permission to Lambda function: $FUNCTION_NAME"
aws lambda add-permission \
    --function-name "$FUNCTION_NAME" \
    --statement-id "$STATEMENT_ID" \
    --action "lambda:InvokeFunction" \
    --principal events.amazonaws.com \
    --source-arn "arn:aws:events:$REGION:$ACCOUNT_ID:rule/$RULE_NAME" \
    --region "$REGION"

# Step 4: Add Lambda function as the target for the EventBridge rule
echo "Adding Lambda function: $FUNCTION_NAME as target for EventBridge rule: $RULE_NAME"
aws events put-targets \
    --rule "$RULE_NAME" \
    --targets "Id"="$TARGET_ID","Arn"="arn:aws:lambda:$REGION:$ACCOUNT_ID:function:$FUNCTION_NAME" \
    --region "$REGION"

echo "Setup completed successfully."


# You can run it using a command: sh scripts/setup_eventbridge.sh
