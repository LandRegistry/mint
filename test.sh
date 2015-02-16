#!/usr/bin/env bash

source ./environment-test.sh
py.test --junitxml=results.xml --cov application tests
