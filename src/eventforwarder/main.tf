variable "lambda_iam_role" {
  default=""
}

variable "appsyncapi_url" {
  default=""
}

variable "region" {
  default="us-east-1"
}

variable "apiId" {
  default=""
}

resource "aws_lambda_function" "appsync_eventforwarder" {
  filename         = "appsync_eventforwarder.zip"
  function_name    = "appsync_eventforwarder"
  role             = "${var.lambda_iam_role}"
  handler          = "index.handler"
  source_code_hash = "${filebase64sha256("appsync_eventforwarder.zip")}"
  runtime          = "python3.6"

  environment {
    variables = {
      appsync_url = "${var.appsyncapi_url}"
      region = "${var.region}"
      appsync_api_id = "${var.apiId}"
    }
  }
}

resource "aws_cloudwatch_event_rule" "secretmngr_updates" {
  depends_on=["aws_lambda_function.appsync_eventforwarder"]
  name        = "secretmngr_update_events"
  description = "Capture Updates to secret managers"

  event_pattern = <<PATTERN
{
  "source": [
    "aws.secretsmanager"
  ]
}
PATTERN
}

resource "aws_lambda_permission" "secretmngr_updates_permission" {
  statement_id = "secretmngr_updates_permission"
  action = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.appsync_eventforwarder.function_name}"
  principal = "events.amazonaws.com"
  source_arn = "${aws_cloudwatch_event_rule.secretmngr_updates.arn}"
}

resource "aws_lambda_permission" "s3_updates_permission" {
  statement_id = "s3_updates_permission"
  action = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.appsync_eventforwarder.function_name}"
  principal = "s3.amazonaws.com"
}

resource "aws_cloudwatch_event_target" "appsync_eventforwarder_target" {
  rule      = "${aws_cloudwatch_event_rule.secretmngr_updates.name}"
  target_id = "SendToLambda"
  arn       = "${aws_lambda_function.appsync_eventforwarder.arn}"
}
