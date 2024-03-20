import pandas as pd
import numpy as np
import sys
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import OneHotEncoder

from flask import Blueprint, jsonify, request
from joblib import dump, load


model = load('./api/model_save.joblib')
passenger = pd.DataFrame({
    'pclass': [1],
    'sex': [0],
    'age': [5],
    'sibsp': [0],
    'parch': [0],
    'fare': [512.00],
    'alone': [0]
})

titanic_api = Blueprint('titanic_api', __name__, url_prefix='/api/titanic')

@titanic_api.route('/api/titanic/predict', methods=['POST'])
def predict():
    data = request.json
    if data is None:
        return jsonify({'error': 'No data provided'}), 400
    
    dead_proba, alive_proba = np.squeeze(model.predict_proba(data))

    return jsonify({'alive_chance': alive_proba, 'dead_chance': dead_proba}), 200