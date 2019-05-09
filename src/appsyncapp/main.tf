variable "lambda_iam_role" {
  default=""
}

variable "appsync_iam_role" {
  default=""
}

resource "aws_appsync_graphql_api" "appsync_config" {
  authentication_type = "API_KEY"
  name                = "appsync_config"
  schema              = <<EOF
type Mutation {
  updateResource(id: ID!, data: String): Resource!
}

type Query {
  getResource(id: ID!, data: String): Resource!
}

type Resource {
  id: ID!
  data: String!
}

type Subscription {
  updatedResource(id: ID): Resource
    @aws_subscribe(mutations: ["updateResource"])
}

schema {
  query: Query
  mutation: Mutation
  subscription: Subscription
}
EOF
}

resource "aws_appsync_resolver" "test" {
  api_id           = "${aws_appsync_graphql_api.appsync_config.id}"
  field            = "updateResource"
  type             = "Mutation"
  data_source      = "${aws_appsync_datasource.appsync_lambda_datasource.name}"
  request_template = <<EOF
{
  "version" : "2017-02-28",
  "operation": "Invoke",
  "payload": $util.toJson($context.args)
}
EOF
  response_template = <<EOF
$util.toJson($context.result)
EOF
}


resource "aws_appsync_datasource" "appsync_lambda_datasource" {
  api_id      = "${aws_appsync_graphql_api.appsync_config.id}"
  name        = "appsync_lambda_datasource"
  type        = "AWS_LAMBDA"
  service_role_arn = "${var.lambda_iam_role}"
  lambda_config {
    function_arn = "${aws_lambda_function.appsync_datasource.arn}"
  }
}


resource "aws_lambda_function" "appsync_datasource" {
  filename         = "appsync_datasource.zip"
  function_name    = "appsync_datasource"
  role             = "${var.lambda_iam_role}"
  handler          = "appsync_datasource.handler"
  source_code_hash = "${filebase64sha256("appsync_datasource.zip")}"
  runtime          = "python3.6"

}

output "appsyncapi_url" {
  value = "${aws_appsync_graphql_api.appsync_config.uris["GRAPHQL"]}"
}

output "appsyncapi_id" {
  value = "${aws_appsync_graphql_api.appsync_config.id}"
}
