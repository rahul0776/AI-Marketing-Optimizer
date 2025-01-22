import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

# Load dataset
data = pd.read_csv("../data/superstore_data.csv")

# Remove leading/trailing spaces from column names
data.columns = data.columns.str.strip()

# Debugging: Check updated column names
print("Columns in the dataset:")
print(data.columns)

# Handle missing values
imputer = SimpleImputer(strategy="median")
data["Income"] = imputer.fit_transform(data[["Income"]])

# Drop irrelevant columns
data = data.drop(columns=["Id", "Dt_Customer"], errors="ignore")

# Create new features
data["Age"] = 2025 - data["Year_Birth"]
data["Total_Spend"] = (
    data["MntWines"] + data["MntFruits"] + data["MntMeatProducts"] +
    data["MntFishProducts"] + data["MntSweetProducts"] + data["MntGoldProds"]
)
data["Family_Size"] = data["Kidhome"] + data["Teenhome"] + 2

# Encode categorical columns
categorical_cols = ["Education", "Marital_Status"]
encoder = OneHotEncoder(sparse_output=False)
encoded_cols = pd.DataFrame(
    encoder.fit_transform(data[categorical_cols]),
    columns=encoder.get_feature_names_out(categorical_cols)
)
data = pd.concat([data, encoded_cols], axis=1)
data = data.drop(columns=categorical_cols)

# Scale numerical columns
scaler = StandardScaler()
scaled_cols = ["Income", "Recency", "Total_Spend", "Age"]
data[scaled_cols] = scaler.fit_transform(data[scaled_cols])

# Save preprocessed data
output_path = "../data/preprocessed_superstore_data.csv"
data.to_csv(output_path, index=False)
print(f"Preprocessed dataset saved to {output_path}")
