from flask import Flask, render_template, jsonify
import psutil
import subprocess

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/system")
def get_pi_mri():
    cpu_usage = psutil.cpu_percent(interval=1)
    temperature = psutil.sensors_temperatures().get('cpu_thermal', [])[0].current if psutil.sensors_temperatures() else "N/A"
    wifi_strength = subprocess.check_output("iwconfig wlan0 | grep 'Signal level'", shell=True).decode('utf-8').strip()
    
    # For the ESP32, you would need to check its status using serial communication or API request
    esp_status = "Connected"  # You can change this based on actual ESP32 status (for example, check if connected)

    health_data = {
        "cpu_usage": cpu_usage,
        "temperature": temperature,
        "wifi_strength": wifi_strength,
        "esp_status": esp_status
    }

    return jsonify(health_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

