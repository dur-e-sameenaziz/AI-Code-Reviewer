.PHONY: run migrate test check

run:
	python manage.py runserver

migrate:
	python manage.py migrate

test:
	python manage.py test

check:
	python manage.py check
