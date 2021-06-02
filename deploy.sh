#!/usr/bin/bash

@echo OFF

waitress-serve --host=0.0.0.0 --port=5000 beebeesee:app

@echo ON