import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_curve, auc
import matplotlib.pyplot as plt
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split
from imblearn.combine import SMOTEENN
from sklearn.model_selection import TimeSeriesSplit
import numpy as np
file_path = '/Users/arshelmelfor/Downloads/cleaned_data_zone.csv'
data = pd.read_csv(file_path, encoding='latin1', sep=';')

data = data[data['eco_zone'] == 'Caribbean']

# Define recession: Two consecutive years of GDP drop
data['is_recession'] = data['recession_flag'] == 1
# Fill NaN values resulting from shifting
data.fillna(0, inplace=True)

# Feature Engineering: Create additional economic indicators
data['emp_ratio'] = data['pop'] / data['emp']  # Employment-to-population ratio
# data['investment_change'] = data['csh_m'].diff()  # Change in investment

# Drop rows with missing values generated by diff()
data.dropna(inplace=True)

# Define features and target variable
X = data[['emp_ratio', 'csh_m', 'cda','pl_n','cn','ck','pl_x']]  # Exclude 'gdp_change' to prevent leakage
y = data['is_recession']
if np.any(np.isinf(X)) or np.any(np.isnan(X)):
    print("X contains invalid values (inf or NaN). Cleaning data...")
    
    # Replace inf/-inf with NaN
    X.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # Replace NaN with 0 (or use an appropriate strategy like imputation)
    X.fillna(0, inplace=True)
# Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
rf_classifier = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight='balanced',
    max_depth=5,
    min_samples_split=10,
)
rf_classifier.fit(X_train, y_train)

tscv = TimeSeriesSplit(n_splits=3)

# Iterate over train-test splits
for fold, (train_index, test_index) in enumerate(tscv.split(X)):
    print(f"Fold {fold + 1}")
    
    # Split the data
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

    
   # Initialize SMOTE with k_neighbors=1
    smote = SMOTE(random_state=42, k_neighbors=1)

    # Pass the SMOTE instance to SMOTEENN
    smote_enn = SMOTEENN(random_state=42, smote=smote)
    
    # Test the model
    y_prob = rf_classifier.predict_proba(X_test)[:, 1]

# Adjust the threshold
    threshold = 0.6  
    y_pred_adjusted = (y_prob > threshold).astype(int)
    
    # Evaluate the model
    # print(f"Accuracy for Fold {fold + 1}: {accuracy_score(y_test, y_pred)}")
    # print(f"Classification Report for Fold {fold + 1}:\n{classification_report(y_test, y_pred, zero_division=1)}")
    print("Accuracy with Adjusted Threshold:", accuracy_score(y_test, y_pred_adjusted))
    print("Classification Report with Adjusted Threshold:\n", classification_report(y_test, y_pred_adjusted, zero_division=1))