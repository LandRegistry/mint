#!/usr/bin/env bash

source ./environment-test.sh
py.test --junitxml=TEST-mint.xml --cov application tests
