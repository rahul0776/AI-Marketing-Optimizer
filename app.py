import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from PIL import Image

# Load the saved model and feature names
model = joblib.load("./models/best_model.pkl")
feature_names = joblib.load("./models/feature_names.pkl")

# Set page configuration
st.set_page_config(
    page_title="AI-Powered Marketing Campaign Optimizer",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add a centered banner using Streamlit's layout features
banner = Image.open("./assets/banner.png")  # Replace with your banner file
with st.container():
    centered_banner = st.columns([1, 2, 1])  # Create three columns
    with centered_banner[1]:  # Center column
        st.image(banner, use_container_width=True, caption="AI-Powered Marketing Campaign Optimizer")

# Define the app header
st.title("AI-Powered Marketing Campaign Optimizer")
st.markdown("### Optimize your marketing efforts by predicting campaign responders with precision.")

st.markdown("---")

# Use columns to split layout
col1, col2 = st.columns([3, 1])

# Left Column: Upload Data
with col1:
    st.subheader("Upload Data & Generate Predictions")
    uploaded_file = st.file_uploader("Upload your campaign dataset (CSV format):", type="csv")
    
    if uploaded_file:
        st.write("### Uploaded Dataset Preview")
        data = pd.read_csv(uploaded_file)
        st.dataframe(data.head(10))
        st.write("### Dataset Summary")
        st.dataframe(data.describe())

        # Add progress indicator
        with st.spinner("Processing predictions..."):
            data = data.reindex(columns=feature_names, fill_value=0)
            data["Prediction"] = model.predict(data)
            data["Confidence"] = model.predict_proba(data).max(axis=1)

        st.success("Predictions generated successfully!")
        st.subheader("Predictions with Confidence Scores")
        st.dataframe(data)

        # Add a bar chart summarizing predictions
        st.subheader("Prediction Summary")
        prediction_counts = data["Prediction"].value_counts()
        st.bar_chart(prediction_counts)

        # Display KPI metrics
        responders = prediction_counts.get(1, 0)
        non_responders = prediction_counts.get(0, 0)
        total = responders + non_responders
        col1.metric("Responders", responders)
        col1.metric("Non-Responders", non_responders)
        col1.metric("Total Predictions", total)

        # Download Predictions
        st.download_button(
            label="Download Predictions as CSV",
            data=data.to_csv(index=False),
            file_name="predictions.csv",
            mime="text/csv"
        )

# Sidebar: Feature Explanation
st.sidebar.header("Feature Explanation")
st.sidebar.markdown("""
- **Recency**: Days since the customer's last purchase.
- **Income**: Annual income of the customer in dollars.
- **Age**: Age of the customer in years.
- **Total Spend**: Total amount spent by the customer across all categories.
- **NumWebPurchases**: Number of purchases made through the web.
- **NumStorePurchases**: Number of purchases made in stores.
- **Family Size**: Total number of family members.
""")

st.markdown("---")

# Sidebar: Single Prediction
st.sidebar.header("Campaign Input Features")
st.sidebar.markdown("Enter customer details to predict their response:")
def user_input_features():
    inputs = {
        "Recency": st.sidebar.slider("Recency (Days since last purchase)", 0, 365, 50),
        "Income": st.sidebar.number_input("Income (Annual Income in $)", min_value=0, value=30000),
        "Age": st.sidebar.slider("Age", 18, 100, 40),
        "Total_Spend": st.sidebar.number_input("Total Spend ($)", min_value=0, value=500),
        "NumWebPurchases": st.sidebar.slider("Number of Web Purchases", 0, 20, 5),
        "NumStorePurchases": st.sidebar.slider("Number of Store Purchases", 0, 20, 5),
        "Family_Size": st.sidebar.slider("Family Size", 1, 10, 3),
    }
    return pd.DataFrame(inputs, index=[0])

input_df = user_input_features()
if st.sidebar.button("Predict"):
    st.sidebar.write("### Input Data")
    st.sidebar.dataframe(input_df)

    input_df = input_df.reindex(columns=feature_names, fill_value=0)
    prediction = model.predict(input_df)
    prediction_proba = model.predict_proba(input_df)[0]
    prediction_label = "Responder" if prediction[0] == 1 else "Non-Responder"

    st.sidebar.write(f"### Predicted Response: {prediction_label}")
    st.sidebar.write(f"- Non-Responder Confidence: {prediction_proba[0]:.2f}")
    st.sidebar.write(f"- Responder Confidence: {prediction_proba[1]:.2f}")

# Feature Importance Section
st.subheader("Feature Importance")
importances = model.feature_importances_
importance_df = pd.DataFrame({
    "Feature": feature_names,
    "Importance": importances
}).sort_values(by="Importance", ascending=False)

st.write("### Feature Importance Table")
st.dataframe(importance_df)

# Plot feature importance
plt.figure(figsize=(8, 5))
plt.barh(importance_df["Feature"], importance_df["Importance"], color='skyblue')
plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("Feature Importance")
st.pyplot(plt)
