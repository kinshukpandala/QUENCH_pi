from flask import Flask, render_template, jsonify, request, make_response, redirect
import psutil
import subprocess
import serial.tools.list_ports

app.secret_key = 'hello_my_flag_is_water' 
ADMIN_COOKIE_VALUE = 'admin-xyz-9876-token'

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

# Step 1: Route to set the admin cookie
@app.route('/activatenfc')
def set_admin_cookie():
    resp = make_response(render_template('login_success.html'))  # This page tells the admin the cookie is set
    resp.set_cookie(
        'auth_token',  # Cookie name
        ADMIN_COOKIE_VALUE,  # Your unique admin token
        max_age=60*60*24*30,  # Cookie expires in 30 days
        secure=True,  # Only sent over HTTPS
        httponly=True,  # JavaScript can't read this cookie
        samesite='Strict'  # Sent only in first-party context
    )
    return resp

# Step 2: Protect the admin route with the cookie check
@app.route('/admin')
def admin_panel():
    token = request.cookies.get('auth_token')  # Get the cookie from the request
    if token == ADMIN_COOKIE_VALUE:  # If the cookie matches the secret admin value
        return render_template("index.html")  # Show the admin panel
    else:
        return render_template("access_denied.html"), 403  # Show access denied

# Step 3: Optional route to log out and clear the cookie
@app.route('/deactiveate_nfc')
def logout_admin():
    resp = make_response("You are now logged out.")
    resp.set_cookie("auth_token", '', expires=0)  # Remove the cookie
    return resp

if __name__ == '__main__':
    app.run()
    