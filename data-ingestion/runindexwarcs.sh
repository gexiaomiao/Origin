#!/bin/bash

source ./index_env.sh

python indexwarcsjob.py \
--conf-path ./mrjob.conf \
--cdx_bucket=$WARC_CDX_BUCKET \
--no-output \
--cmdenv AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
--cmdenv AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
-r emr $WARC_MANIFEST &> /tmp/emrrun.log &
