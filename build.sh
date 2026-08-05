#!/usr/bin/env bash
set -ex
apt-get update -y
apt-get install -y ffmpeg
pip install -r bot/requirements.txt