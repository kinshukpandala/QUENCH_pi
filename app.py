from flask import Flask, render_template, jsonify, request, make_response
import psutil
import subprocess
import serial.tools.list_ports

app = Flask(__name__)
app.secret_key = 'hello_my_flag_is_water'

# Your admin cookie secret value
ADMIN_COOKIE_VALUE = 'admin-xyz-9876-token'

# Checks if ESP32 is connected via serial
def is_serial_connected():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "USB" in port.device or "ttyUSB" in port.device:
            return True
    return False

# ---------- Main Routes ---------- #

@app.route("/")
def home():
    return render_template("index.html")  # Your landing page

@app.route("/about")
def about():
    return render_template("about.html")  # Your about page

@app.route("/system")
def get_pi_mri():
    try:
        mem = psutil.virtual_memory()
        temperature = psutil.sensors_temperatures().get('cpu_thermal', [])[0].current if psutil.sensors_temperatures() else "N/A"

        try:
            wifi_info = subprocess.check_output("iwconfig wlan0 | grep 'Signal level'", shell=True).decode('utf-8').strip()
        except subprocess.CalledProcessError:
            wifi_info = "Unavailable"

        esp_status = "Connected" if is_serial_connected() else "Disconnected"

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

# ---------- Authentication System ---------- #

#Visit this once to set the admin cookie (manually, not via NFC)
@app.route('/activatenfc')
def set_admin_cookie():
    resp = make_response(render_template('login_success.html'))  # Show success
    resp.set_cookie(
        'auth_token',
        ADMIN_COOKIE_VALUE,
        max_age=60*60*24*30,  # 30 days
        secure=True,          # Required for HTTPS
        httponly=True,
        samesite='Lax'        # Allows cookie via NFC tap and link
    )
    return resp

#This is what your NFC tag points to URL: https://iot.thequench.shop/admin
@app.route('/admin')
def admin_panel():
    token = request.cookies.get('auth_token')
    if token == ADMIN_COOKIE_VALUE:
        return render_template("index.html")  # Authenticated view
    else:
        return render_template("access_denied.html"), 403  # Denied

# Optional: Visit site to Logout and clear the admin cookie
@app.route('/deactivate_nfc')
def logout_admin():
    resp = make_response("You are now logged out.")
    resp.set_cookie("auth_token", '', expires=0)
    return resp

# Visit Site for debugging route to test cookie presence 
@app.route('/check-auth')
def check_auth():
    token = request.cookies.get('auth_token')
    if token == ADMIN_COOKIE_VALUE:
        return "✅ Authenticated"
    else:
        return "❌ Not Authenticated"

# ---------- Run the Flask App on localhost port 5000 hosting via cloudflared---------- #
if __name__ == '__main__':
    app.run()
