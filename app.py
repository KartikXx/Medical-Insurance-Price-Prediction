from flask import Flask, request, render_template, redirect, url_for, session
import numpy as np
import joblib
import os

app = Flask(__name__, template_folder='./templates', static_folder='./static')
app.secret_key = 'a2487d88633fd6739411225096900872'  # Change this to a random secret in production

# Hardcoded credentials for demo
USERNAME = 'admin'
PASSWORD = 'password'

# Path to the model file
Pkl_Filename = os.path.join(os.path.dirname(__file__), "rf_tuned.pkl")

# Try loading the model with joblib
try:
    model = joblib.load(Pkl_Filename)
except FileNotFoundError:
    print(f"Error: Model file {Pkl_Filename} not found.")
    model = None
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('home'))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('home.html')

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if not model:
        return render_template('op.html', pred='Error: Model not loaded.')

    try:
        features = [int(x) for x in request.form.values()]
        final = np.array(features).reshape((1, 6))
        pred = model.predict(final)[0]
        if pred < 0:
            return render_template('op.html', pred='Error calculating Amount!')
        else:
            return render_template('op.html', pred='Expected amount is {0:.3f}'.format(pred))
    except Exception as e:
        print(f"Error in prediction: {e}")
        return render_template('op.html', pred='Error processing the input.')

if __name__ == '__main__':
    app.run(debug=True)