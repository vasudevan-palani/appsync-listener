#!/bin/bash
mkdir .tmp
cd .tmp
cp -rf ../../src/* .
cp ../*.py .
cp ../*.txt .
if [ ! -d deps ]
then
  pip3 install -t deps -r eventforwarder/requirements.txt --no-cache
  pip3 install -t deps -r testrequirements.txt --no-cache
fi
pytest -s -v *_test.py
