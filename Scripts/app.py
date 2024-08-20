import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.graph_objects as go
import subprocess
import sqlitecloud
from dotenv import load_dotenv

# Function to load predictions from database
def load_predictions(connection_string, table_name='waves'):
    # Open the connection to SQLite Cloud
    conn = sqlitecloud.connect(connection_string)
    
    # Use the correct database
    db_name = "chinook.sqlite"
    conn.execute(f"USE DATABASE {db_name}")
    
    try:
        # Load data from the specified table into a pandas DataFrame
        query = f"SELECT * FROM {table_name}"
        predictions = pd.read_sql_query(query, conn)
        
        # Convert the 'datetime' column to a datetime object and set it as the index
        predictions['datetime'] = pd.to_datetime(predictions['datetime'])
        predictions.set_index(keys='datetime', inplace=True)
        predictions.sort_index(ascending=True, inplace=True)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        predictions = pd.DataFrame()  # Return an empty DataFrame if an error occurs
    
    finally:
        # Close the database connection
        conn.close()
    
    return predictions

# Optional: Function to trigger prediction script manually
# def run_prediction_script():
#     result = subprocess.run(['python', 'predict.py'], capture_output=True, text=True)
#     st.text(f"Output:\n{result.stdout}")
#     st.text(f"Errors (if any):\n{result.stderr}")

# Streamlit app layout
st.title("Model Predictions")

# Display the last update time (if applicable)
st.write("Last updated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Load and display the latest predictions
load_dotenv()
connection_string = os.getenv('SQL_CONNECTION')
predictions = load_predictions(connection_string = connection_string)
last_preds = predictions[:-24]

if not predictions.empty:
    st.write("Latest Predictions:")

    # Wave height
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
                    y=last_preds['wave_height'], 
                    x=last_preds.index,
                    mode='lines',
                    name='Predicted Height',
                    line=dict(color='royalblue'))) 
    fig1.update_layout(
        title='Predicted wave heights in Mooloolaba',
        xaxis_title="Date/Time",
        yaxis_title="Wave height (meters)",
    )
    st.plotly_chart(fig1, use_container_width=True)

    # Wave period
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
                    y=last_preds['wave_period'], 
                    x=last_preds.index,
                    mode='lines',
                    name='Predicted period',
                    line=dict(color = 'orange')))
    fig2.update_layout(
        title='Predicted wave period in Mooloolaba',
        xaxis_title="Date/Time",
        yaxis_title="Wave period (seconds)",
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Wave direction
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
                    y=last_preds['wave_direction'], 
                    x=last_preds.index,
                    mode='lines',
                    name='Predicted direction of waves',
                    line=dict(color = 'green')))
    fig3.update_layout(
        title='Predicted direction of waves in Mooloolaba',
        xaxis_title="Date/Time",
        yaxis_title="Direction of waves (degrees, N=0, E=90)",
    )
    st.plotly_chart(fig3, use_container_width=True)

else:
    st.write("No predictions available yet.")

st.dataframe(last_preds)
st.dataframe(predictions)

# Optional: Button to manually run the prediction script
# if st.button('Run Predictions Now'):
#     run_prediction_script()

# Optional: Button to refresh the predictions display
# if st.button('Refresh Predictions'):
#     predictions = load_predictions()
#     st.write("Latest Predictions:")
#     st.dataframe(predictions)
