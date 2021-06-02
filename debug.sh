#!/usr/bin/bash

@echo OFF

export FLASK_APP=beebeesee
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000

@echo ON