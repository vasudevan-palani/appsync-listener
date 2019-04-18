#!/bin/bash

if [ "$#" -ne 1 ]; then
  echo "deploy script needs 1 arguments: <stage>"
  exit 1;
fi

stage=$1

cd src/appsyncapp
zip -r ../appsync_datasource.zip appsync_datasource.py
cd ../eventforwarder
#pip3 install -t deps -r requirements.txt --no-cache
ls -ltr deps/
zip -r ../appsync_eventforwarder.zip *.py *.conf deps/**
cd ..

rm -rf .terraform

terraform init -backend-config="key=terraform/appsync-listener-${stage}.json" -input=false
terraform apply -auto-approve -var-file=${stage}.vars
