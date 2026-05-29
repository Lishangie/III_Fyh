# Итоговый проект по курсу «Инженерия Искусственного Интеллекта»

---

## 1. Паспорт проекта

- **Название проекта:** `Кредитный скоринг: сервис оценки риска невозврата кредита`
- **Автор:** `Фех Алексей Александрович`
- **Группа:** `ИМБО-02-24`
- **Контакт:** `@Lishangie`

- **Краткое описание (2-4 предложения):**
  Проект посвящён построению сервиса кредитного скоринга, который оценивает вероятность невозврата кредита (дефолта) по профилю клиента и параметрам заявки. Используются открытые данные German Credit Risk из репозитория UCI/OpenML, классические ML-модели (логистическая регрессия, случайный лес, градиентный бустинг) и простая нейросеть (MLP). Результат — REST API на FastAPI, упакованный в Docker, который по признакам заявки возвращает вероятность дефолта и категорию риска.

---

## 2. Структура проекта

```
project/
├── README.md                — паспорт проекта и инструкции по запуску
├── report.md                — отчёт по проекту (постановка, данные, эксперименты, результаты)
├── self-checklist.md        — чеклист самопроверки
├── requirements.txt         — зависимости проекта
├── Dockerfile               — Docker-образ для сервиса
├── docker-compose.yml       — Docker Compose для запуска
├── notebooks/
│   ├── 01_eda.ipynb         — разведочный анализ данных
│   └── 02_baselines.ipynb   — эксперименты с моделями и сравнение
├── src/
│   ├── __init__.py
│   ├── config.py            — конфигурация проекта
│   ├── data/
│   │   ├── __init__.py
│   │   ├── loader.py        — загрузка и генерация данных
│   │   └── preprocessing.py — предобработка признаков
│   ├── models/
│   │   ├── __init__.py
│   │   ├── train.py         — обучение и сохранение моделей
│   │   └── predict.py       — загрузка модели и предсказание
│   └── service/
│       ├── __init__.py
│       └── app.py           — FastAPI-сервис
├── data/
│   ├── README.md            — описание данных
│   └── download_data.py     — скрипт загрузки/генерации данных
├── configs/
│   ├── config.yaml          — конфигурация моделей и сервиса
│   └── .env.example         — шаблон переменных окружения
├── tests/
│   ├── __init__.py
│   ├── test_data.py         — тесты модуля данных
│   ├── test_model.py        — тесты модели
│   └── test_service.py      — тесты API-сервисa
└── artifacts/
    └── README.md            — описание артефактов
```

---

## 3. Требования и установка

### 3.1. Требования

- Python `>= 3.10`
- Docker (для контейнерного запуска)
- Git

### 3.2. Установка окружения

```bash
# Перейти в папку проекта
cd project

# Создать виртуальное окружение
python -m venv .venv

# Активировать окружение:
# Linux / macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Установить зависимости
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 4. Как запустить проект

### 4.1. Подготовка данных

```bash
cd project
source .venv/bin/activate
python data/download_data.py
```

Скрипт загрузит датасет German Credit Risk из OpenML и сохранит его в `data/german_credit.csv`.

### 4.2. Обучение модели

```bash
cd project
source .venv/bin/activate
python -m src.models.train
```

Скрипт обучит все модели, сравнит их по метрикам, сохранит лучшую в `artifacts/model.pkl` и выведет таблицу результатов.

### 4.3. Запуск сервиса (локально)

```bash
cd project
source .venv/bin/activate
python -m src.service.app
```

Сервис поднимется на порту `8000`. Доступные эндпоинты:
- `GET /health` — проверка работоспособности
- `POST /predict` — предсказание риска дефолта

Пример запроса к `/predict`:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "checking_account": "A11",
    "duration": 6,
    "credit_history": "A34",
    "purpose": "A43",
    "credit_amount": 1169,
    "savings_account": "A65",
    "employment_since": "A75",
    "installment_rate": 4,
    "personal_status": "A93",
    "other_debtors": "A101",
    "residence_since": 4,
    "property": "A121",
    "age": 67,
    "other_installment_plans": "A143",
    "housing": "A152",
    "existing_credits": 2,
    "job": "A173",
    "people_liable": 1,
    "telephone": "A192",
    "foreign_worker": "A201"
  }'
```

Ответ:

```json
{
  "default_probability": 0.12,
  "risk_category": "low",
  "model_name": "RandomForestClassifier"
}
```

### 4.4. Запуск через Docker

```bash
cd project
docker build -t credit-scoring .
docker run -p 8000:8000 credit-scoring
```

Или через Docker Compose:

```bash
cd project
docker-compose up --build
```

После запуска Swagger UI доступен по адресу: `http://localhost:8000/docs`

---

## 5. Данные

Для обучения используется открытый датасет **German Credit Risk** из репозитория UCI/OpenML.

- **Источник:** [OpenML - German Credit Risk](https://www.openml.org/d/31)
- **Объём:** 1000 записей, 20 признаков + целевая переменная
- **Тип задачи:** бинарная классификация (1 = хороший заёмщик, 2 = плохой заёмщик)
- **Файлы данных:**
  - `data/german_credit.csv` — полный датасет (загружается скриптом `data/download_data.py`)

Датасет не содержит персональных данных и является открытым, что соответствует правилам курса.

---

## 6. Тесты

В проекте реализованы тесты:

- **test_data.py** — тесты загрузки и предобработки данных
- **test_model.py** — тесты обучения и предсказания модели
- **test_service.py** — тесты API-эндпоинтов

Запуск тестов:

```bash
cd project
source .venv/bin/activate
pytest tests/ -v
```

---

## 7. Демонстрация на защите

На защите я планирую продемонстрировать:

1. **Структуру проекта** — краткий обзор `notebooks/`, `src/`, `data/`, `configs/`, `tests/`.
2. **Ноутбук EDA** — покажу ключевые визуализации и выводы из `notebooks/01_eda.ipynb`.
3. **Сравнение моделей** — покажу таблицу метрик из `notebooks/02_baselines.ipynb` и `report.md`.
4. **Запуск сервиса** — запущу API через Docker, отправлю тестовые запросы через Swagger UI.
5. **Наблюдаемость** — покажу логи запросов и эндпоинт `/health`.
6. **Тесты** — запущу `pytest` и покажу, что все тесты проходят.

---

## 8. Ограничения и дальнейшая работа

**Текущие ограничения:**
- Используется один датасет (German Credit Risk); для продакшена потребуется больше данных.
- Сервис работает синхронно; для высокой нагрузки нужна асинхронная обработка.
- Нет авторизации и аутентификации запросов.

**Направления развития:**
- Добавить несколько алгоритмов с выбором через конфигурацию
- Реализовать хранение истории запросов в базе данных
- Добавить авторизацию (API-ключи / JWT)
- Реализовать Prometheus-метрики и Grafana-дашборд
- Добавить MLflow для трекинга экспериментов
- Реализовать A/B тестирование моделей

---

## 9. Оценка проекта

Итоговая оценка за проект выставляется по пятибалльной шкале (2-5). Детали — в `self-checklist.md` и `evaluation/project-evaluation.md` методического репозитория.
