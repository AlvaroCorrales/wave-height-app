import streamlit as st
import pandas as pd
import os
from datetime import datetime
import subprocess

# Function to load predictions from a CSV or another data source
def load_predictions(prediction_file='../Data/predictions/predictions.csv'):
    if os.path.exists(prediction_file):
        predictions = pd.read_csv(prediction_file)
    else:
        predictions = pd.DataFrame()  # Return an empty DataFrame if no predictions exist
    return predictions

# Optional: Function to trigger prediction script manually
def run_prediction_script():
    result = subprocess.run(['python', 'predict.py'], capture_output=True, text=True)
    # st.text(f"Output:\n{result.stdout}")
    # st.text(f"Errors (if any):\n{result.stderr}")

# Streamlit app layout
st.title("Model Predictions")

# Display the last update time (if applicable)
st.write("Last updated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Load and display the latest predictions
predictions = load_predictions()

if not predictions.empty:
    st.write("Latest Predictions:")
    st.dataframe(predictions)
else:
    st.write("No predictions available yet.")

# Optional: Button to manually run the prediction script
if st.button('Run Predictions Now'):
    run_prediction_script()

# Optional: Button to refresh the predictions display
if st.button('Refresh Predictions'):
    predictions = load_predictions()
    st.write("Latest Predictions:")
    st.dataframe(predictions)
