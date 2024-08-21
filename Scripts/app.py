import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.graph_objects as go
import subprocess
import sqlitecloud
from dotenv import load_dotenv

## DEFINITIONS
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
        predictions.sort_index(ascending=False, inplace=True)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        predictions = pd.DataFrame()  # Return an empty DataFrame if an error occurs
    
    finally:
        # Close the database connection
        conn.close()
    
    return predictions

# Map direction names
def name_my_direction(deg:float):
    '''
    Maps directions in degrees to direction names (north, south, etc.)
    '''
    
    if 0 <= deg < 22.5:
        dir = 'NORTH'
    elif 22.5 <= deg < 67.5:
        dir = 'NORTHEAST'
    elif 67.5 <= deg < 112.5:
        dir = 'EAST'
    elif 112.5 <= deg < 157.5:
        dir = 'SOUTHEAST'
    elif 157.5 <= deg < 202.5:
        dir = 'SOUTH'
    elif 202.5 <= deg < 247.5:
        dir = 'SOUTHWEST'
    elif 247.5 <= deg < 292.5:
        dir = 'WEST'
    elif 292.5 <= deg < 337.5:
        dir = 'NORTHWEST'
    elif 337.5 <= deg < 360:
        dir = 'NORTH'
    else:
        dir = 'ERROR'
    return dir

# Optional: Function to trigger prediction script manually
# def run_prediction_script():
#     result = subprocess.run(['python', 'predict.py'], capture_output=True, text=True)
#     st.text(f"Output:\n{result.stdout}")
#     st.text(f"Errors (if any):\n{result.stderr}")

## INTERFACE
st.title('Can I surf in Queensland? 🏄‍♂️')
st.write("Check surfing conditions in Queensland's best surfing spots")
st.selectbox('Select your location', ['Mooloolaba', 'Brisbane'])

tab1, tab2, tab3 = st.tabs(['About', 'Charts', 'Data'])

# TAB 1
tab1.header('About')
tab1.write('In this website you can check the wave height, period and direction 12-hour forecasts of beaches in Queensland, Australia.')
tab1.write('Feel like catching some waves? 🌊😎☀️')
tab1.markdown('> This app is under construction. Stay tuned for updates and be kind with errors and lack of features.')

# TAB 2
tab2.header("Model Predictions")

# Display the last update time (if applicable)
# tab2.write("Last updated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Load and display the latest predictions
load_dotenv()
connection_string = os.getenv('SQL_CONNECTION')
predictions = load_predictions(connection_string = connection_string)
last_preds = predictions[:-24]

if not predictions.empty:
    # tab2.write("Latest Predictions:")

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
    tab2.plotly_chart(fig1, use_container_width=True)

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
    tab2.plotly_chart(fig2, use_container_width=True)

    # Wave direction    
    all_directions = ['NORTH', 'NORTHEAST', 'EAST', 'SOUTHEAST', 'SOUTH', 'SOUTHWEST', 'WEST', 'NORTHWEST']
    direction_mapping = {direction: i for i, direction in enumerate(all_directions)}
    last_preds['direction_string'] = last_preds['wave_direction'].apply(lambda x: name_my_direction(x))
    last_preds['direction_code'] = last_preds['direction_string'].map(direction_mapping)

    fig3 = go.Figure()
    # Add the line with markers
    fig3.add_trace(go.Scatter(
        x=last_preds.index,
        y=last_preds['direction_code'],
        mode='lines+markers',
        marker=dict(size=10),
        line=dict(width=2),
        text=last_preds['direction_string'],  # Hover text will show the direction
        hoverinfo='text'
    ))
    fig3.update_layout(
        title='Predicted direction that waves are coming from',
        xaxis_title='Time',
        yaxis_title='Direction',
        yaxis=dict(
            tickvals=[0, 1, 2, 3, 4, 5, 6, 7],  # Corresponding codes for NORTH, EAST, SOUTH, WEST
            ticktext=all_directions,  # Explicitly set tick labels
        ),
    )

    # Show the figure
    tab2.plotly_chart(fig3, use_container_width=True)
 

else:
    st.write("No predictions available yet.")

# Optional: Button to manually run the prediction script
# if st.button('Run Predictions Now'):
#     run_prediction_script()

# Optional: Button to refresh the predictions display
# if st.button('Refresh Predictions'):
#     predictions = load_predictions()
#     st.write("Latest Predictions:")
#     st.dataframe(predictions)

# TAB 3
tab3.header('Model Predictions')
tab3.write(last_preds[['wave_height', 'wave_period', 'wave_direction', 'direction_string']].rename(columns = 
    {'wave_height': 'Wave height (meters)',
     'wave_direction': 'Wave direction (degrees)',
     'wave_period': 'Wave period (seconds)',
     'direction_string': 'Wave direction'}
))