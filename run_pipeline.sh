#!/bin/bash
export GITHUB_PAT="$(cat /root/.github_pat)"
python3.12 /root/mmofinds/affiliate_pipeline.py
