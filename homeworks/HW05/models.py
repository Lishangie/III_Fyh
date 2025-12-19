"""ML Models for HW05"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler


class ModelEnsemble:
    """Энсамбль моделей"""
    
    def __init__(self):
        self.models = {
            'lr': LogisticRegression(random_state=42, max_iter=1000),
            'rf': RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1),
            'gb': GradientBoostingClassifier(n_estimators=100, random_state=42),
        }
        self.scaler = StandardScaler()
        self.results = {}
    
    def fit(self, X_train, y_train):
        """Обучить все модели"""
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        for name, model in self.models.items():
            if name == 'lr':
                model.fit(X_train_scaled, y_train)
            else:
                model.fit(X_train, y_train)
            
            scores = cross_val_score(model, X_train_scaled if name == 'lr' else X_train, 
                                    y_train, cv=5, scoring='roc_auc')
            self.results[name] = {
                'model': model,
                'cv_scores': scores,
                'cv_mean': scores.mean(),
                'cv_std': scores.std()
            }
            print(f"{name}: CV ROC-AUC = {scores.mean():.4f} (+/- {scores.std():.4f})")
    
    def predict(self, X_test):
        """Предсказы"""
        predictions = {}
        for name, result in self.results.items():
            model = result['model']
            if name == 'lr':
                X_test_scaled = self.scaler.transform(X_test)
                predictions[name] = model.predict_proba(X_test_scaled)[:, 1]
            else:
                predictions[name] = model.predict_proba(X_test)[:, 1]
        return predictions
