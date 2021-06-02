@echo OFF

set FLASK_APP=beebeesee
set FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000

@echo ON