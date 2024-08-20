import pickle
import sqlitecloud
import numpy as np
import pandas as pd
import urllib.request
import urllib.parse
import json
from dotenv import load_dotenv
import os

# Step 1: Load the trained model from the pickle file
def load_model(model_path):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    return model

# Step 2: Fetch data from the data API
def fetch_data():
    # Base URL and resource ID
    base_url = 'https://www.data.qld.gov.au/api/3/action/datastore_search'
    resource_id = '2bbef99e-9974-49b9-a316-57402b00609c'

    # Define the filter query for the site "Mooloolaba"
    filters = {
        "Site": "Mooloolaba"
    }

    # Define the parameters, including the resource ID and the filters
    params = {
        'resource_id': resource_id,
        'limit': 48,  # 48 records for the last 24 hours with 30 min intervals
        'q': json.dumps(filters),  # Convert the filters dictionary to a JSON string                
        'sort': '_id desc'  # Sort by record ID in descending order to get the latest records  # Convert the filters dictionary to a JSON string
    }

    # Encode the parameters and create the full URL
    url = f"{base_url}?{urllib.parse.urlencode(params)}"

    # Initialize the dictionary to store results
    result_dict = {}

    # Make the request
    try:
        fileobj = urllib.request.urlopen(url)
        response = fileobj.read()
        data = json.loads(response)
        
        # Store the records in the dictionary
        for record in data.get('result', {}).get('records', []):
            record_id = record.get('_id')
            result_dict[record_id] = record
                
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code} - {e.reason}")
    except Exception as e:
        print(f"Error: {e}")

    return result_dict

# Step 3: Preprocess the data if necessary
def preprocess_data(result_dict):
    
    # Conversion to dataframe
    df = pd.DataFrame.from_dict(result_dict, orient='index')

    # Renaming
    df.rename(columns = {
        'DateTime':'datetime',
        'Hmax':'wave_height',
        'Tz':'wave_period',
        'Direction': 'wave_direction'
    }, inplace = True)

    # Timestamp format
    df['datetime'] = pd.to_datetime(df['datetime'])
    # df['DateTime'] = df['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')    
    df.set_index(keys = 'datetime', inplace=True)
    df = df.asfreq('30T')

    # Keep only desired variables
    target_vars = ['wave_height', 'wave_period', 'wave_direction']
    df = df[target_vars]

    # Null values
    df = df.replace(-99.9, np.nan)

    return df

# Step 4: Make predictions using the loaded model
def make_predictions(model, processed_data):
    predictions = model.predict(steps = 24, last_window=processed_data)
    predictions.index.name = 'datetime'
    predictions.index = predictions.index.strftime('%Y-%m-%d %H:%M:%S')
    return predictions

# Step 5: Insert predictions in database
def upsert_dataframe(connection_string, dataframe):
    # Connect to the SQLiteCloud database
    conn = sqlitecloud.connect(connection_string)
    db_name = "chinook.sqlite"
    conn.execute(f"USE DATABASE {db_name}")
    
    # Define the upsert function inside the main function
    def upsert_row(conn, datetime, wave_direction, wave_height, wave_period):
        upsert_sql = f'''
        INSERT INTO waves (datetime, wave_direction, wave_height, wave_period)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(datetime) DO UPDATE SET
            wave_direction=excluded.wave_direction,
            wave_height=excluded.wave_height,
            wave_period=excluded.wave_period;
        '''
        conn.execute(upsert_sql, (datetime, wave_direction, wave_height, wave_period))
    
    try:
        # Iterate over each row in the dataframe and perform the upsert
        for index, row in dataframe.iterrows():
            upsert_row(conn, index, row['wave_direction'], row['wave_height'], row['wave_period'])
        
        print("Data appended and updated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

# Step 5: Main function to execute the steps
def main():
    # Load the model
    model_path = 'Models/mooloolaba/forecaster_mool.pkl'
    model = load_model(model_path)

    # Fetch the data
    data = fetch_data()

    # Preprocess the data
    processed_data = preprocess_data(data)

    # Make predictions
    predictions = make_predictions(model, processed_data)

    # Save the predictions to a file, database, etc.
    load_dotenv()
    connection_string = os.getenv('SQL_CONNECTION')
    print(connection_string[0:2])
    # upsert_dataframe(connection_string, predictions)

    # Print the predictions
    # print("Predictions:")
    # print(predictions)

if __name__ == '__main__':
    main()
