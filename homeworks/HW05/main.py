#!/usr/bin/env python3
"""Основной скрипт для запуска HW05"""

import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split
from models import ModelEnsemble
from utils import evaluate_model, get_feature_importance
from prepare_data import *


def main():
    print("=" * 60)
    print("HW05: Credit Risk Prediction")
    print("=" * 60)
    
    # Лоад конфиг
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    print("\n[✓] Config loaded")
    
    # Загружаем данные
    df = pd.read_csv('data.csv')
    print(f"[✓] Data loaded: {df.shape}")
    print(f"  - Defaults: {df['default'].sum()} ({df['default'].mean():.1%})")
    
    # Подготовка
    X = df.drop(columns=['client_id', 'default'])
    y = df['default']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=1 - config['data']['train_size'],
        random_state=config['data']['random_state'],
        stratify=y
    )
    
    print(f"[✓] Data split: train={X_train.shape[0]}, test={X_test.shape[0]}")
    
    # Обучение
    print("\n[✓] Training ensemble...")
    ensemble = ModelEnsemble()
    ensemble.fit(X_train, y_train)
    
    # Предсказы
    print("\n[✓] Making predictions...")
    predictions = ensemble.predict(X_test)
    
    from sklearn.metrics import roc_auc_score
    print("\nTest Results:")
    for name, proba in predictions.items():
        auc = roc_auc_score(y_test, proba)
        print(f"  - {name}: ROC-AUC = {auc:.4f}")
    
    print("\n[✓] Done")


if __name__ == '__main__':
    main()
