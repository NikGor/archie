# Makefile for Archie Document Management System
# Система управления документами с функциями сканирования и обработки

.PHONY: help install install-dev test lint format run run-dev clean \
		migrate makemigrations shell superuser \
		build build-dev run-docker stop-docker \
		collectstatic \
		add-commit push deploy \
		scan-documents process-documents backup-db \
		documents-status documents-cleanup test-llm \
		scanner-check scanner-install scanner-test

# Переменные
PROJECT_NAME = archie
DOCKER_IMAGE = archie-dms
DOCKER_CONTAINER = archie-dms-container
POETRY = poetry
PYTHON = $(POETRY) run python
MANAGE = $(PYTHON) manage.py

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
BLUE = \033[0;34m
NC = \033[0m # No Color

help: ## Показать справку по командам
	@echo "$(BLUE)Archie Document Management System$(NC)"
	@echo "$(GREEN)Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости проекта
	@echo "$(GREEN)Устанавливаю зависимости Archie DMS...$(NC)"
	$(POETRY) install

install-dev: ## Установить зависимости для разработки
	@echo "$(GREEN)Устанавливаю зависимости для разработки...$(NC)"
	$(POETRY) install --with dev

check: ## Проверить конфигурацию Django
	@echo "$(GREEN)Проверяю конфигурацию Django...$(NC)"
	$(MANAGE) check

test: ## Запустить тесты
	@echo "$(GREEN)Запускаю тесты системы управления документами...$(NC)"
	$(MANAGE) test --verbosity=2

test-llm: ## Тестировать LLM сервис
	@echo "$(GREEN)Тестирую LLM сервис...$(NC)"
	$(PYTHON) test_llm.py

lint: ## Проверить код с помощью flake8
	@echo "$(GREEN)Проверяю код Archie DMS...$(NC)"
	$(POETRY) run flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	$(POETRY) run flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format: ## Форматировать код с помощью black
	@echo "$(GREEN)Форматирую код Archie DMS...$(NC)"
	$(POETRY) run black .
	$(POETRY) run isort .

run: ## Запустить сервер разработки Archie DMS
	@echo "$(GREEN)Запускаю Archie Document Management System...$(NC)"
	$(MANAGE) runserver

run-dev: ## Запустить сервер разработки с автоматической перезагрузкой
	@echo "$(GREEN)Запускаю Archie DMS с автоперезагрузкой...$(NC)"
	$(POETRY) run python manage.py runserver --noreload

migrate: ## Применить миграции базы данных
	@echo "$(GREEN)Применяю миграции базы данных Archie...$(NC)"
	$(MANAGE) makemigrations
	$(MANAGE) migrate

makemigrations: ## Создать новые миграции
	@echo "$(GREEN)Создаю миграции для Archie DMS...$(NC)"
	$(MANAGE) makemigrations

shell: ## Открыть Django shell для работы с документами
	@echo "$(GREEN)Открываю Django shell для Archie DMS...$(NC)"
	$(MANAGE) shell

superuser: ## Создать суперпользователя для Archie DMS
	@echo "$(GREEN)Создаю суперпользователя для Archie DMS...$(NC)"
	$(MANAGE) createsuperuser

collectstatic: ## Собрать статические файлы
	@echo "$(GREEN)Собираю статические файлы Archie DMS...$(NC)"
	$(MANAGE) collectstatic --noinput

clean: ## Очистить временные файлы и кэш
	@echo "$(GREEN)Очищаю временные файлы Archie DMS...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type f -name ".DS_Store" -delete
	@echo "$(YELLOW)Очистка завершена$(NC)"

# Специфичные команды для Archie DMS
scan-documents: ## Сканировать и обработать документы
	@echo "$(GREEN)Запускаю сканирование документов...$(NC)"
	@if [ -f scan_documents.py ]; then \
		$(PYTHON) scan_documents.py; \
	else \
		echo "$(YELLOW)Скрипт сканирования не найден. Создайте scan_documents.py$(NC)"; \
	fi

process-documents: ## Обработать загруженные документы
	@echo "$(GREEN)Обрабатываю загруженные документы...$(NC)"
	@if [ -f process_documents.py ]; then \
		$(PYTHON) process_documents.py; \
	else \
		echo "$(YELLOW)Скрипт обработки не найден. Создайте process_documents.py$(NC)"; \
	fi

backup-db: ## Создать резервную копию базы данных
	@echo "$(GREEN)Создаю резервную копию базы данных Archie...$(NC)"
	@mkdir -p backups
	$(MANAGE) dumpdata > backups/archie_backup_$(shell date +%Y%m%d_%H%M%S).json
	@echo "$(GREEN)Резервная копия создана в папке backups/$(NC)"

# Команды для работы со сканером
scanner-check: ## Проверить доступность сканера
	@echo "$(GREEN)Проверяю доступность сканера...$(NC)"
	@if [ -f scan_documents.py ]; then \
		$(PYTHON) -c "from scan_documents import DocumentScanner; scanner = DocumentScanner(); print('✅ Сканер доступен' if scanner._check_scanner_available() else '❌ Сканер не найден')"; \
	else \
		echo "$(YELLOW)Скрипт сканирования не найден$(NC)"; \
	fi

scanner-install: ## Установить зависимости для сканера
	@echo "$(GREEN)Устанавливаю зависимости для сканера...$(NC)"
	@echo "$(BLUE)Для Linux (Ubuntu/Debian):$(NC)"
	@echo "sudo apt-get update"
	@echo "sudo apt-get install sane-utils xsane libsane-dev"
	@echo "$(BLUE)Для Windows:$(NC)"
	@echo "pip install pywin32"
	@echo "$(BLUE)Для macOS:$(NC)"
	@echo "brew install sane-backends"

scanner-test: ## Протестировать сканер
	@echo "$(GREEN)Тестирую сканер...$(NC)"
	@if [ -f scan_documents.py ]; then \
		$(PYTHON) scan_documents.py; \
	else \
		echo "$(YELLOW)Скрипт сканирования не найден$(NC)"; \
	fi

# Docker команды для Archie DMS
build: ## Собрать Docker образ Archie DMS
	@echo "$(GREEN)Собираю Docker образ Archie Document Management System...$(NC)"
	docker build -t $(DOCKER_IMAGE) .

build-dev: ## Собрать Docker образ для разработки
	@echo "$(GREEN)Собираю Docker образ для разработки Archie DMS...$(NC)"
	docker build -t $(DOCKER_IMAGE)-dev --target development .

run-docker: ## Запустить Archie DMS в Docker
	@echo "$(GREEN)Запускаю Archie DMS в Docker...$(NC)"
	docker run -d --name $(DOCKER_CONTAINER) -p 8000:8000 -v $(PWD)/documents:/app/documents $(DOCKER_IMAGE)

stop-docker: ## Остановить Docker контейнер Archie DMS
	@echo "$(GREEN)Останавливаю Docker контейнер Archie DMS...$(NC)"
	docker stop $(DOCKER_CONTAINER) || true
	docker rm $(DOCKER_CONTAINER) || true

# Git команды
add-commit: ## Добавить изменения и создать коммит
	@echo "$(GREEN)Добавляю изменения в Git...$(NC)"
	git add .
	@read -p "Введите сообщение коммита: " message; \
	git commit -m "$$message"

push: ## Отправить изменения в репозиторий
	@echo "$(GREEN)Отправляю изменения в репозиторий...$(NC)"
	git push origin main

# Развертывание
deploy: ## Развернуть Archie DMS
	@echo "$(GREEN)Развертываю Archie Document Management System...$(NC)"
	@if [ -f deploy.py ]; then \
		$(PYTHON) deploy.py; \
	else \
		echo "$(YELLOW)Файл deploy.py не найден. Создайте скрипт развертывания.$(NC)"; \
	fi

# Комбинированные команды для Archie DMS
setup: install migrate collectstatic ## Полная настройка Archie DMS
	@echo "$(GREEN)Archie Document Management System настроен!$(NC)"
	@echo "$(BLUE)Доступен по адресу: http://localhost:8000$(NC)"

dev-setup: install-dev migrate collectstatic ## Настройка для разработки
	@echo "$(GREEN)Archie DMS настроен для разработки!$(NC)"

check: lint test ## Проверить код и запустить тесты
	@echo "$(GREEN)Проверка Archie DMS завершена!$(NC)"

docker-setup: build run-docker ## Настроить и запустить Archie DMS в Docker
	@echo "$(GREEN)Archie DMS запущен в Docker на http://localhost:8000$(NC)"

full-backup: backup-db collectstatic ## Полная резервная копия системы
	@echo "$(GREEN)Полная резервная копия Archie DMS создана!$(NC)"

# Команды для работы с документами
documents-status: ## Показать статус документов
	@echo "$(GREEN)Статус документов в Archie DMS:$(NC)"
	$(MANAGE) shell -c "from archie.documents.models import Document; print(f'Всего документов: {Document.objects.count()}')"

documents-cleanup: ## Очистить старые документы
	@echo "$(GREEN)Очищаю старые документы...$(NC)"
	@read -p "Введите количество дней для удаления старых документов: " days; \
	$(MANAGE) shell -c "from datetime import datetime, timedelta; from archie.documents.models import Document; Document.objects.filter(date__lt=datetime.now()-timedelta(days=$$days)).delete(); print('Очистка завершена')"