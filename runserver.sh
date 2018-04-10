#!/bin/sh
DIR_HOME=$(pwd)/backend
export PYTHONPATH="${PYTHONPATH}:DIR_HOME"
python backend/run.py
