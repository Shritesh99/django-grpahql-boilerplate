.Default: run

run:
	python manage.py runserver

kill:
	kill -9 $(lsof -ti :8000)