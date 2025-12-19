# HW05: Инженерия AI - Credit Risk Prediction

Студент: Фех Алексей Александрович  
Группа: ИМБО-02-24

## Структура

- `notebook.ipynb` - основной ноутбук с анализом и моделями
- `prepare_data.py` - скрипт для загрузки датасета
- `requirements.txt` - зависимости
- `data.csv` - датасет (загружается автоматически)

## Использование

```bash
# Установить зависимости
pip install -r requirements.txt

# Загрузить датасет
python prepare_data.py

# Запустить ноутбук
jupyter notebook notebook.ipynb
```

## Описание

Анализ данных о кредитных клиентах и предсказание вероятности дефолта.

### Этапы анализа:
1. EDA (Exploratory Data Analysis)
2. Подготовка данных
3. Обучение моделей (Logistic Regression, Random Forest)
4. Оценка производительности (ROC-AUC, Classification Report)
5. Анализ важности признаков
