# Stock Market Trading App - Mid-Term Index Reconstitution Strategy

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/django-4.2+-green.svg)](https://www.djangoproject.com/)
[![Status](https://img.shields.io/badge/status-active--development-orange.svg)]()

## 📊 Overview

A Django REST API backend for algorithmic stock trading strategies focused on mid-term index reconstitution events. This application provides machine learning-based trading signals, price predictions, and stock screening capabilities designed for US equity markets.

**Public Repository:** [Algo-Stock-Trading](https://github.com/Jamuna-KC/Algo-Stock-Trading)

---

## 🏗️ Architecture

trading_api/
├── manage.py
├── README.md
├── requirements.txt
├── architecture/
│ ├── api_structure.md
│ └── system_design.md
├── trading_api/
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
└── strategies/
├── model
.py ├──
iews.py ├── se
ializers.py
├── urls.p
├── ml_models/ │
├── pivot_strategy.py
│ ├── price_prediction.
y │ ├──
tock_screener.py │ └──
saved/

---

## 📚 Reference Notebooks

This project is based on three core Jupyter notebooks demonstrating trading strategies:

### 1. [Filtering_methods.ipynb](https://github.com/Jamuna-KC/Algo-Stock-Trading/blob/main/Filtering_methods.ipynb)
- **Purpose:** Stock screening based on fundamental metrics
- **Features:**
  - Filters by P/E ratio, ROE, ROCE, volume, and price
  - Identifies high-quality investment opportunities
  - Customizable multi-criteria screening

### 2. [Next_Day_Stock_Price_Prediction.ipynb](https://github.com/Jamuna-KC/Algo-Stock-Trading/blob/main/Next_Day_Stock_Price_Prediction.ipynb)
- **Purpose:** Machine learning models for next-day price movement prediction
- **Models:**
  - Logistic Regression
  - Support Vector Machine (SVM)
  - XGBoost Classifier
- **Features:** OHLCV feature engineering and ensemble predictions

### 3. [Pivot_Point_Algorithm.ipynb](https://github.com/Jamuna-KC/Algo-Stock-Trading/blob/main/Pivot_point_algorithm.ipynb)
- **Purpose:** Technical analysis using pivot points
- **Features:**
  - Calculates support and resistance levels
  - Generates Buy/Hold/Sell signals
  - Decision Tree classifier for signal prediction

---

## 🚀 Features

### Core Strategies

#### 1. **Pivot Point Trading Strategy**
- Calculates pivot points, support (S1, S2), and resistance (R1, R2) levels
- Provides Buy/Hold/Sell trading signals
- ML-based signal prediction using Decision Tree
- Real-time trade recommendations

#### 2. **Next-Day Price Prediction**
- Ensemble prediction combining multiple models
- Predicts Up/Down price movement
- Confidence-weighted majority voting
- Model accuracy tracking

#### 3. **Stock Screener**
- Multi-criteria filtering (price, P/E, ROE, ROCE, volume)
- Custom sorting and pagination
- Top stocks by performance metrics
- Detailed company fundamentals

---

## 🔌 API Endpoints

### Base URL
http://localhost:8000/api/
