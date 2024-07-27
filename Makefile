.PHONY: install test lint run clean

install:
	poetry install

check:
	poetry run python manage.py check

test:
	poetry run python manage.py test

lint:
	poetry run flake8

run:
	poetry run python manage.py runserver

clean:
	find . -name "*.pyc" -delete

migrate:
	poetry run python manage.py makemigrations
	poetry run python manage.py migrate

add-and-commit:
	git add .
	git commit --amend --no-edit
	git push --force

build:
	docker build -t django-app .

deploy:
	@python deploy.py