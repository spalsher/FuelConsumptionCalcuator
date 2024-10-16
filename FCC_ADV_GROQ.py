# app.py
from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a real secret key

# Fuel characteristics
FUEL_CHARACTERISTICS = {
    'Diesel': {'density': 0.832, 'carbon_content': 0.86},
    'Petrol': {'density': 0.745, 'carbon_content': 0.85}
}

class EngineForm(FlaskForm):
    hc = FloatField('Hydrocarbons (HC) in PPM', validators=[DataRequired(), NumberRange(min=0)])
    nox = FloatField('Nitrogen Oxides (NOx) in PPM', validators=[DataRequired(), NumberRange(min=0)])
    co = FloatField('Carbon Monoxide (CO) in %', validators=[DataRequired(), NumberRange(min=0, max=100)])
    co2 = FloatField('Carbon Dioxide (CO2) in %', validators=[DataRequired(), NumberRange(min=0, max=100)])
    o2 = FloatField('Oxygen (O2) in %', validators=[DataRequired(), NumberRange(min=0, max=100)])
    engine_type = SelectField('Engine Type', choices=[('Truck', 'Truck'), ('Genset', 'Genset')], validators=[DataRequired()])
    engine_capacity = FloatField('Engine Capacity (kW)', validators=[DataRequired(), NumberRange(min=0)])
    engine_size = FloatField('Engine Size (L)', validators=[DataRequired(), NumberRange(min=0)])
    engine_rpm = FloatField('Engine RPM', validators=[DataRequired(), NumberRange(min=0)])
    engine_load = FloatField('Engine Load (%)', validators=[DataRequired(), NumberRange(min=0, max=100)])
    fuel_type = SelectField('Fuel Type', choices=[('Diesel', 'Diesel'), ('Petrol', 'Petrol')], validators=[DataRequired()])
    test_type = SelectField('Test Type', choices=[('pre', 'Pre-emission'), ('post', 'Post-emission')], validators=[DataRequired()])
    submit = SubmitField('Calculate')

def calculate_fuel_consumption(data):
    # This is a simplified calculation and should be replaced with a more accurate model
    emissions_factor = (data['hc'] + data['nox']) / 1000000 + data['co'] / 100 + data['co2'] / 100
    engine_factor = data['engine_capacity'] * data['engine_size'] * (data['engine_rpm'] / 1000) * (data['engine_load'] / 100)
    fuel_factor = FUEL_CHARACTERISTICS[data['fuel_type']]['density'] * FUEL_CHARACTERISTICS[data['fuel_type']]['carbon_content']
    
    consumption = emissions_factor * engine_factor * fuel_factor
    
    if data['engine_type'] == 'Genset':
        return consumption  # L/h
    else:  # Truck
        return consumption / 100  # L/km (assuming 100 km/h average speed for simplification)

@app.route('/', methods=['GET', 'POST'])
def index():
    form = EngineForm()
    result = None
    if form.validate_on_submit():
        data = {
            'hc': form.hc.data,
            'nox': form.nox.data,
            'co': form.co.data,
            'co2': form.co2.data,
            'o2': form.o2.data,
            'engine_type': form.engine_type.data,
            'engine_capacity': form.engine_capacity.data,
            'engine_size': form.engine_size.data,
            'engine_rpm': form.engine_rpm.data,
            'engine_load': form.engine_load.data,
            'fuel_type': form.fuel_type.data
        }
        consumption = calculate_fuel_consumption(data)
        result = f"Fuel consumption: {consumption:.2f} {'L/h' if data['engine_type'] == 'Genset' else 'L/km'}"
    return render_template('index.html', form=form, result=result)

if __name__ == '__main__':
    app.run(debug=True)

