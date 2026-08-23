#!/bin/bash
set -e
cd backend
pip install --upgrade pip
pip install --only-binary :all: -r requirements.txt || pip install -r requirements.txt
