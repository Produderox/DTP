from flask import Flask, render_template, url_for ,jsonify, request
from logging import FileHandler,WARNING
from sqlalchemy import create_engine, text
import csv
import os
import joblib
import numpy as np
import sklearn

app = Flask(__name__,static_folder="/Static")

app = Flask(__name__, template_folder = 'template')
file_handler = FileHandler('errorlog.txt')
file_handler.setLevel(WARNING)

engine = create_engine('sqlite:///database.db')
model = joblib.load('trained_linear_regression_model.pkl')
print(f"Model type: {type(model)}")

def read_csv(file_path):
    data = []
    try:
        with open(file_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)  # Read CSV as a dictionary
            for row in csv_reader:
                data.append(row)
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
    return data

def get_all_countries():
     with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM Country"))
        columns = result.keys()  
        data = [dict(zip(columns, row)) for row in result.fetchall()]  
        countries = list(set(row['Country'] for row in data))  
        countries.sort() 
        return countries

def get_production(selected_country):
    with engine.connect() as conn:
        result = conn.execute(
            text("""SELECT Country, "Production (t)" AS Production, "Corn Type" 
                    FROM Country 
                    WHERE Country = :country AND Year = 2021"""),
            {"country": selected_country}
        )
        data = [dict(row._mapping) for row in result.fetchall()]
        return data

def get_rain(selected_country):
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT DISTINCT Country, "Year", "Annual Precipitation(mm)"
                FROM Country 
                WHERE Country = :country
                """
            ),
            {"country": selected_country}
        )
        data = [dict(row._mapping) for row in result.fetchall()]
    return data

def land_water_data(selected_country):
    with engine.connect() as conn:
            # Execute the query to fetch data
            result = conn.execute(
                text("""
                    SELECT DISTINCT Country, "Water per Capita", "Agricultural land (sq. km)"
                    FROM Country
                    WHERE Country = :country AND Year=2021
                """),
                {"country": selected_country}
            )

            # Format the result into a list of dictionaries
            data = [dict(row._mapping) for row in result.fetchall()]
    return data

def crop_needs(selected_country):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT DISTINCT Country, "Freshwater Withdrawal", "Fertilizer (kg/ha)"
                FROM Country 
                WHERE Country = :country And Year=2021
            """),
            {"country": selected_country}
        )

        data = [dict(row._mapping) for row in result.fetchall()]
    return data

def crop_yield(selected_country):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT DISTINCT Country, "Corn Type", "Yield (kg/ha)", Year
                FROM Country 
                WHERE Country = :country
            """),
            {"country": selected_country}
        )

        data = [dict(row._mapping) for row in result.fetchall()]
    return data

@app.route('/<path:path>')
def static_file(path):
    return app.send_static_file(path) 

@app.route('/')
def index():
    image_folder = os.path.join('static', 'Image')
    images = [os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    csv_path = os.path.join(app.static_folder, 'GFSI_2022.csv')  # Adjust path
    csv_data = read_csv(csv_path)  # Read the CSV data
    return render_template('index.html',images=images,data=csv_data)

@app.route('/stats')
def stats():
    return render_template('stats.html',countries=get_all_countries())

@app.route('/results', methods=['POST'])
def query():
    selected_country = request.form.get('dropdown')
    return render_template('results.html',countries=get_all_countries(),selected_country=selected_country, production=get_production(selected_country),
                           rain=get_rain(selected_country),land=land_water_data(selected_country),crop=crop_needs(selected_country),crop_yield=crop_yield(selected_country))

@app.route('/prediction')
def prediction():
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT DISTINCT "Corn Type"
                FROM Country 
            """)
        )
        data = [dict(row._mapping) for row in result.fetchall()]
    return render_template('prediction.html',croptype=data)

@app.route('/predict_result', methods=['POST'])
def predict_result():

    query = text("""
        SELECT Country,"Yield (kg/ha)"
        FROM Country
        WHERE year = 2021 AND "Corn Type" = 'Wheat'
    """)

    # Execute the query and fetch results
    with engine.connect() as conn:
        result = conn.execute(query)
        data = [dict(row._mapping) for row in result.fetchall()] 

    countries = [item['Country'] for item in data]
    yields = [item['Yield (kg/ha)'] for item in data]

    # Retrieve form data
    rainfall = request.form.get('rainfall')  # Use the `name` attribute from the form
    max_temperature = request.form.get('max-temperature') 
    min_temperature = request.form.get('min-temperature') # Use the `name` attribute from the form
    crop = request.form.get('crop')  # Use the `name` attribute from the dropdown

    # Convert inputs to the correct types
    rainfall = float(rainfall)
    max_temperature = float(max_temperature)
    min_temperature = float(min_temperature)

    crop_mapping = {"Maize": 0, "Wheat": 1, "Rice": 2}  
    crop_encoded = crop_mapping.get(crop, -1)

    # Prepare input features as a 2D array
    input_features = np.array([[min_temperature, max_temperature,rainfall]])  

    # Predict using the model
    prediction = model.predict(input_features)
    print(prediction)

    data_for_plot = {
        'countries': countries,
        'yields': yields
    }

    return render_template('predict_result.html', prediction=prediction[0], data_for_plot=data_for_plot)

if __name__ =="__main__":
    app.run(debug=True)