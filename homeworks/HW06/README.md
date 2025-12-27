# HW06: Decision Trees and Ensembles

## Структура

- `HW06.ipynb` - основной ноутбук с анализом
- `report.md` - отчет по результатам
- `artifacts/` - папка с артефактами эксперимента
  - `metrics_test.json` - финальные метрики на test
  - `search_summaries.json` - лучшие параметры моделей
  - `best_model.joblib` - сохраненная лучшая модель
  - `best_model_meta.json` - метаданные лучшей модели
  - `figures/` - графики
    - `roc_curves.png` - ROC-кривые всех моделей
    - `confusion_matrix.png` - confusion matrix лучшей модели
    - `feature_importance.png` - важность признаков
- `S06-hw-dataset-02.csv` - датасет

## Задание

Сравнение моделей машинного обучения:

1. Загрузить датасет S06-hw-dataset-02 и выполнить EDA
2. Разделить на train/test с фиксированным random_state
3. Построить baseline модели (DummyClassifier, LogisticRegression)
4. Реализовать DecisionTree с контролем сложности
5. Сравнить ансамбли: RandomForest, GradientBoosting
6. Оценить модели по Accuracy, F1, ROC-AUC
7. Построить ROC-кривые и confusion matrix
8. Проанализировать важность признаков

## Запуск

```bash
# Просто откройте ноутбук и выполните все ячейки
jupyter notebook HW06.ipynb
```

## Результаты

Лучшая модель: **GradientBoostingClassifier**
- ROC-AUC: 0.8712
- Accuracy: 0.8578
- F1-score: 0.6921
