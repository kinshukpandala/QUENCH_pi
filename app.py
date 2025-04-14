from flask import Flask, render_template, jsonify
import psutil
import subprocess
import serial.tools.list_ports

app = Flask(__name__)

def is_serial_connected():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB" in port.device or "ttyUSB" in port.device:
            return True
    return False

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/system")
def get_pi_mri():
    try:
        mem = psutil.virtual_memory()
        temperature = psutil.sensors_temperatures().get('cpu_thermal', [])[0].current if psutil.sensors_temperatures() else "N/A"

        # Wi-Fi signal strength
        try:
            wifi_info = subprocess.check_output("iwconfig wlan0 | grep 'Signal level'", shell=True).decode('utf-8').strip()
        except subprocess.CalledProcessError:
            wifi_info = "Unavailable"

        esp_status = "Connected" if is_serial_connected() else "Disconnected"

        # Format the health data (removed hostname, platform, and architecture)
        health_data = {
            "wifi_strength": wifi_info,
            "esp_status": esp_status, 
            "cpu_temperature": temperature,
            "memory_used": round(mem.used / (1024 ** 3), 2),
            "memory_total": round(mem.total / (1024 ** 3), 2),
        }

    except Exception as e:
        health_data = {"error": str(e)}

    return jsonify(health_data)

if __name__ == '__main__':
    app.run()
    