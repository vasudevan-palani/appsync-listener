variable "lambda_iam_role" {
  default=""
}

variable "appsync_iam_role" {
  default=""
}

variable "app" {
  default="appsync-listener"
}

variable "region" {
  default="us-east-2"
}

variable "stage" {
  default=""
}

variable "bucket_name" {
  default=""
}

variable "dynamodb_table" {
  default=""
}

#======================Used for local run only===========================
terraform {
  backend "s3" {
    bucket = "tfstates.ssm.com"
    region = "us-east-2"
    dynamodb_table = "tfstates"
    profile = "default"
  }
}

provider "aws" {
  region                  = "${var.region}"
  shared_credentials_file = "~/.aws/creds"
  profile                 = "default"
}

provider "aws" {
  alias  = "us-east-2"
  region = "us-east-2"
}

data "terraform_remote_state" "network" {
  backend = "s3"
  config {
    bucket = "tfstates.ssm.com"
    key    = "terraform/ecs-${var.app}-${var.stage}.json"
    region = "us-east-2"
    profile = "default"
  }
}

module "appsync_app"{
  source = "appsyncapp"
  lambda_iam_role = "${var.lambda_iam_role}"
  appsync_iam_role = "${var.appsync_iam_role}"
}

module "eventforwarder"{
  source = "eventforwarder"
  lambda_iam_role = "${var.lambda_iam_role}"
  appsyncapi_url = "${module.appsync_app.appsyncapi_url}"
  region = "${var.region}"
  apiId = "${module.appsync_app.appsyncapi_id}"
}
