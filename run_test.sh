#!/bin/sh

TEST_FILTER="("$(yq --output-format=yaml 'join("|")' test_filter.yaml)")"
echo $TEST_FILTER

pushd $HOME/h/source/hyperbase

bin/trigger_build \
    --test_filter="$TEST_FILTER" \
    --coverage \
    --num_attempts 1

popd
