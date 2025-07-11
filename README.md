# Archie Document Management System

Система управления документами с функциями сканирования и обработки с использованием ИИ.

## Описание

Archie - это Django-приложение для управления документами, которое позволяет:

- Загружать и сканировать документы
- Организовывать документы по категориям
- Автоматически генерировать метаданные с помощью ИИ
- Обрабатывать и индексировать документы
- Управлять задачами, связанными с документами
- **Сканировать документы с помощью физического сканера**

## Возможности ИИ

- **Автоматическая генерация названий** документов
- **Умная категоризация** документов
- **Извлечение текста** из изображений (OCR)
- **Анализ содержимого** PDF, DOC, TXT файлов
- **Интеллектуальное описание** документов

## Возможности сканирования

- **Поддержка различных сканеров** (SANE, WIA, Image Capture)
- **Автоматическое определение** доступных сканеров
- **Настройка разрешения** сканирования (72-1200 DPI)
- **Веб-интерфейс** для управления сессиями сканирования
- **Автоматическая обработка** отсканированных документов с помощью ИИ
- **История сканирования** с детальной информацией о сессиях

## Установка

```bash
# Клонирование репозитория
git clone <repository-url>
cd archie

# Установка зависимостей
make install

# Настройка переменных окружения
cp env.example .env
# Отредактируйте .env файл и добавьте ваш OPENAI_API_KEY

# Настройка базы данных
make migrate

# Создание суперпользователя
make superuser

# Запуск сервера
make run
```

## Настройка сканера

### Linux (Ubuntu/Debian)

```bash
# Установка SANE
sudo apt-get update
sudo apt-get install sane-utils xsane libsane-dev

# Проверка доступности сканера
make scanner-check

# Тестирование сканера
make scanner-test
```

### Windows

```bash
# Установка pywin32 для WIA
pip install pywin32

# Проверка доступности сканера
make scanner-check
```

### macOS

```bash
# Установка SANE backends
brew install sane-backends

# Проверка доступности сканера
make scanner-check
```

## Настройка ИИ функций

### 1. Получение OpenAI API ключа

1. Зарегистрируйтесь на [OpenAI Platform](https://platform.openai.com/)
2. Перейдите в раздел [API Keys](https://platform.openai.com/api-keys)
3. Создайте новый API ключ
4. Скопируйте ключ

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```bash
# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# OpenAI API для ИИ функций
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 3. Тестирование ИИ функций

```bash
# Тестирование LLM сервиса
make test-llm
```

## Использование

После запуска приложение будет доступно по адресу: http://localhost:8000

### Загрузка документов с ИИ

1. Перейдите на страницу загрузки документов
2. Включите опцию "Автоматически сгенерировать название, категорию и описание"
3. Загрузите документ (PDF, DOC, DOCX, TXT, JPG, PNG)
4. Система автоматически проанализирует документ и заполнит поля
5. При необходимости отредактируйте сгенерированные данные
6. Сохраните документ

### Сканирование документов

1. Перейдите в раздел "Scanner" в навигации
2. Нажмите "Новое сканирование"
3. Укажите название документа (опционально)
4. Выберите сканер и разрешение
5. Создайте сессию сканирования
6. Нажмите "Выполнить сканирование"
7. Поместите документ в сканер и дождитесь завершения
8. Документ будет автоматически обработан с помощью ИИ

## Команды Makefile

```bash
# Показать справку
make help

# Полная настройка
make setup

# Тестирование ИИ функций
make test-llm

# Работа со сканером
make scanner-check      # Проверить доступность сканера
make scanner-install    # Показать инструкции по установке
make scanner-test       # Протестировать сканер

# Работа с документами
make documents-status
make backup-db

# Docker развертывание
make docker-setup
```

## Поддерживаемые форматы

- **PDF** - извлечение текста и анализ
- **DOC/DOCX** - анализ содержимого
- **TXT** - прямое чтение текста
- **JPG/PNG** - OCR с помощью OpenAI Vision API
- **Отсканированные документы** - автоматическое распознавание и обработка

## Поддерживаемые сканеры

- **SANE** (Linux) - большинство USB и сетевых сканеров
- **WIA** (Windows) - Windows Image Acquisition
- **Image Capture** (macOS) - встроенная система сканирования
- **xsane** (Linux) - графический интерфейс для SANE
- **gscan2pdf** (Linux) - сканирование в PDF

## Технологии

- Django 5.0+
- Python 3.10+
- OpenAI API (GPT-3.5, GPT-4 Vision)
- SANE (Scanner Access Now Easy)
- WIA (Windows Image Acquisition)
- Poetry для управления зависимостями
- Docker для контейнеризации
- Bootstrap для UI

## Безопасность

- API ключи хранятся в переменных окружения
- Документы обрабатываются локально
- Временные файлы автоматически удаляются
- Поддержка HTTPS в продакшене
- Безопасное управление сессиями сканирования

## Лицензия

MIT License
