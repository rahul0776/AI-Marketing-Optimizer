import pandas as pd
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from imblearn.over_sampling import SMOTE
import joblib

# Load preprocessed data
data = pd.read_csv("../data/preprocessed_superstore_data.csv")

# Select relevant features
selected_features = [
    "Recency", "Income", "Age", "Total_Spend",
    "NumWebPurchases", "NumStorePurchases", "Family_Size"
]
X = data[selected_features]
y = data["Response"]

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Handle class imbalance using SMOTE
print("Balancing classes using SMOTE...")
smote = SMOTE(random_state=42)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train, y_train)

# Define the Random Forest model
rf = RandomForestClassifier(random_state=42, class_weight="balanced")

# Define hyperparameter grid for RandomizedSearchCV
param_dist = {
    "n_estimators": [50, 100, 200, 300],
    "max_depth": [None, 10, 20, 30],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
    "bootstrap": [True, False],
}

# Perform hyperparameter tuning
print("Performing hyperparameter tuning...")
random_search = RandomizedSearchCV(
    estimator=rf,
    param_distributions=param_dist,
    n_iter=50,
    cv=3,
    scoring="f1_macro",
    random_state=42,
    n_jobs=-1
)
random_search.fit(X_train_balanced, y_train_balanced)

# Best model from tuning
best_rf_model = random_search.best_estimator_
print("Best hyperparameters:", random_search.best_params_)

# Evaluate the model on the test set
y_pred_best_rf = best_rf_model.predict(X_test)
print("Best Random Forest Performance After Tuning:")
print(classification_report(y_test, y_pred_best_rf))

# Save the tuned model
model_path = "../models/best_model.pkl"
joblib.dump(best_rf_model, model_path)
print(f"Tuned model saved to {model_path}")

# Save feature names for use in the Streamlit app
feature_names_path = "../models/feature_names.pkl"
joblib.dump(selected_features, feature_names_path)
print(f"Selected features saved to {feature_names_path}")
