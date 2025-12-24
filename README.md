# Currency Exchange API (Python)

REST API для обмена валют, написанная Python FastAPI.

## Описание проекта

Проект представляет собой REST API для работы с валютами и курсами обмена. API позволяет:
- Управлять валютами (создание, чтение, обновление, удаление)
- Управлять курсами обмена между валютами
- Выполнять конвертацию валют

Для повышения производительности используется кэширование через Redis.

## Технологический стэк

- **Python 3.8+** - язык программирования
- **FastAPI** - веб-фреймворк для создания API
- **PostgreSQL** - реляционная база данных
- **Redis** - кэш-хранилище для повышения производительности
- **psycopg2** - драйвер для работы с PostgreSQL
- **pydantic** - валидация данных
- **pytest** - фреймворк для тестирования
- **Docker & Docker Compose** - контейнеризация и оркестрация

## Требования

- Python 3.8+
- Docker и Docker Compose (рекомендуется)
- Или PostgreSQL и Redis, установленные локально

## Быстрый запуск с Docker Compose

Самый простой способ запустить проект - использовать Docker Compose:

1. Клонируйте репозиторий (если нужно)

2. Установите зависимости Python:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` и настройте подключение к базе данных:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=db
DB_USER=username
DB_PASSWORD=password
```

4. Запустите PostgreSQL и Redis через Docker Compose:
```bash
docker-compose up -d
```

Это запустит:
- PostgreSQL на порту 5432
- Redis на порту 6379
- RedisInsight (веб-интерфейс для Redis) на порту 8001

5. Создайте базу данных и таблицы (если они еще не созданы):
   - `currencies` (id SERIAL PRIMARY KEY, code VARCHAR(3) UNIQUE, fullname VARCHAR(100), sign VARCHAR(10))
   - `exchangerates` (id SERIAL PRIMARY KEY, basecurrencyid INT REFERENCES currencies(id), targetcurrencyid INT REFERENCES currencies(id), rate DECIMAL)

6. Запустите приложение:
```bash
python main.py
```

Или с помощью uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступен по адресу: **http://localhost:8000**

Документация API (Swagger): **http://localhost:8000/docs**

RedisInsight (веб-интерфейс для Redis): **http://localhost:8001**

## Запуск без Docker Compose

Если вы предпочитаете запускать PostgreSQL и Redis локально:

1. Установите и запустите PostgreSQL

2. Установите и запустите Redis:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis
```

3. Создайте базу данных и таблицы

4. Настройте `.env` файл

5. Запустите приложение:
```bash
python main.py
```

## API Endpoints

### Currencies

- `GET /currencies` - Получить все валюты
- `GET /currency/{id}` - Получить валюту по ID
- `GET /currency?name={code}` - Получить валюту по коду
- `POST /currencies` - Создать валюту
- `PATCH /currencies/{id}` - Обновить валюту
- `DELETE /currencies/{id}` - Удалить валюту

### Exchange Rates

- `GET /exchangeRates` - Получить все курсы обмена
- `GET /exchangeRate/{id}` - Получить курс обмена по ID
- `GET /exchangeRate?name={code}` - Получить курс обмена по коду валютной пары
- `POST /exchangeRates` - Создать курс обмена
- `DELETE /exchangeRates/{id}` - Удалить курс обмена
- `GET /exchange?from={from}&to={to}&amount={amount}` - Конвертировать сумму

## Запуск тестов

Для запуска тестов используется pytest:

1. Убедитесь, что установлены все зависимости (включая тестовые):
```bash
pip install -r requirements.txt
```

2. Запустите все тесты:
```bash
pytest
```

3. Запустите тесты с подробным выводом:
```bash
pytest -v
```

4. Запустите конкретный тестовый файл:
```bash
pytest tests/test_currency_service.py
```

5. Запустите конкретный тест:
```bash
pytest tests/test_currency_service.py::TestCurrencyService::test_find_by_id_cache_hit
```

Тесты используют моки для изоляции тестируемого кода от зависимостей (база данных, Redis).

## Структура проекта

```
currency-exchange-api/
├── src/
│   ├── models/          # Модели данных (Currency, ExchangeRates)
│   ├── dto/             # Data Transfer Objects (ExchangeDTO)
│   ├── repositories/    # Репозитории для работы с БД
│   ├── services/        # Бизнес-логика (с кэшированием Redis)
│   ├── controllers/     # REST API контроллеры
│   ├── util/            # Утилиты (MappingDTO)
│   └── config/          # Конфигурация (database.py, redis.py)
├── tests/               # Тесты
│   └── test_currency_service.py
├── main.py              # Точка входа приложения
├── requirements.txt     # Зависимости Python
├── docker-compose.yaml  # Конфигурация Docker Compose
└── .env                 # Конфигурация БД (не включен в git)
```

## Кэширование

В проекте используется Redis для кэширования данных с целью повышения производительности:

- **CurrencyService**: Кэширует валюты по ID, коду и список всех валют
- **ExchangeRatesService**: Кэширует курсы обмена по ID, коду валютной пары и список всех курсов

Кэш автоматически инвалидируется при изменении данных (создание, обновление, удаление).
TTL кэша по умолчанию: 3600 секунд (1 час).

### Ключи кэша:
- `currency:id:{id}` - валюта по ID
- `currency:code:{code}` - валюта по коду
- `currency:all` - список всех валют
- `exchange_rate:id:{id}` - курс обмена по ID
- `exchange_rate:name:{name}` - курс обмена по коду валютной пары
- `exchange_rate:all` - список всех курсов обмена
