provider "aws" {
  region = var.aws_region
}

resource "aws_s3_bucket" "lambda_bucket" {
  bucket = var.lambda_bucket
}

resource "aws_iam_role" "lambda_role" {
  name               = "handler-lambda-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "s1",
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "lambda_role_policy" {
  name = "lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["secretsmanager:GetSecretValue"]
        Effect   = "Allow"
        Resource = "arn:aws:secretsmanager:ap-southeast-2:639886339024:secret:OPENAI_API_KEY-8ox8rw"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "basic_executionrole" {
  role       = aws_iam_role.lambda_role.id
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "lambda_handler" {
  function_name = "marcio-gh-openai"
  role          = aws_iam_role.lambda_role.arn
  package_type  = "Image"
  memory_size   = 1024
  image_uri     = "639886339024.dkr.ecr.ap-southeast-2.amazonaws.com/marciogh:latest"
  timeout       = 20
}

resource "aws_cloudwatch_log_group" "lambda_cloudwatch_log" {
  name              = "/aws/lambda/${aws_lambda_function.lambda_handler.function_name}"
  retention_in_days = 14
}



resource "aws_iam_role" "api_gateway_cloudwatch" {
  name               = "api-gateway-cloudwatch-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "s1",
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "apigateway.amazonaws.com"
      },
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "api_gateway_cloudwatch_role" {
  role       = aws_iam_role.api_gateway_cloudwatch.id
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}

resource "aws_api_gateway_rest_api" "openai" {
  name        = "marciogh-openai"
  description = "marciogh-openai"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = aws_api_gateway_rest_api.openai.id
  parent_id   = aws_api_gateway_rest_api.openai.root_resource_id
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = aws_api_gateway_rest_api.openai.id
  resource_id   = aws_api_gateway_resource.proxy.id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "proxy_root" {
  rest_api_id   = aws_api_gateway_rest_api.openai.id
  resource_id   = aws_api_gateway_rest_api.openai.root_resource_id
  http_method   = "ANY"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id             = aws_api_gateway_rest_api.openai.id
  resource_id             = aws_api_gateway_method.proxy.resource_id
  http_method             = aws_api_gateway_method.proxy.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.lambda_handler.invoke_arn
}

resource "aws_api_gateway_integration" "lambda_root" {
  rest_api_id             = aws_api_gateway_rest_api.openai.id
  resource_id             = aws_api_gateway_method.proxy_root.resource_id
  http_method             = aws_api_gateway_method.proxy_root.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.lambda_handler.invoke_arn
}

resource "aws_api_gateway_deployment" "openai" {
  depends_on = [
    aws_api_gateway_integration.lambda,
    aws_api_gateway_integration.lambda_root,
  ]
  rest_api_id = aws_api_gateway_rest_api.openai.id
}

resource "aws_api_gateway_stage" "openai_stage" {
  rest_api_id   = aws_api_gateway_rest_api.openai.id
  deployment_id = aws_api_gateway_deployment.openai.id
  stage_name    = "test"
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_handler.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.openai.execution_arn}/*/*"
}

resource "aws_lambda_permission" "cloudwatch" {
  statement_id  = "AllowLogs"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda_handler.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.openai.execution_arn}/*/*"
}

output "base_url" {
  value = aws_api_gateway_deployment.openai.invoke_url
}
output "cloudwatch_role" {
  value = aws_iam_role.api_gateway_cloudwatch.arn
}
