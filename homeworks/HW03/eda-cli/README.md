text
# eda-cli — мини-приложение для EDA

Простой CLI для анализа CSV-датасетов (HW03).

## Установка и запуск

cd homeworks/HW03/eda-cli
uv sync

text

## Команды

### overview
Быстрый обзор датасета (размеры, типы, пропуски, статистика).

uv run eda-cli overview data/example.csv

text

### report
Генерация полного отчёта в Markdown + графики.

uv run eda-cli report data/example.csv --out-dir reports_example

text

#### Новые параметры (HW03):
- `--title "Заголовок"` — кастомный заголовок отчёта (по умолчанию "EDA Report")
- `--min-missing-share 0.2` — порог доли пропусков для "проблемных" колонок (по умолчанию 0.1)

Пример с параметрами:

uv run eda-cli report data/example.csv
--out-dir reports_example
--title "Мой отчёт HW03"
--min-missing-share 0.15

text

## Тесты

uv run pytest -q

text

## Новые эвристики качества данных (HW03)
1. **has_constant_columns** — обнаружение колонок с одинаковыми значениями
2. **has_many_zero_values** — проверка числовых колонок на избыток нулей (порог 60%)