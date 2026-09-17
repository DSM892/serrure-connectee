from flask import Flask, render_template, request, redirect, url_for, session
from database import DatabaseManager
from functools import wraps
from flask import abort
from wifi_packet import Client, WifiPacketError

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = db.get_user_by_id(session['user_id'])
        if not user or user [3] != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return wrapper

IP_ESP32="0.0.0.0"  # Remplacez par l'adresse IP de votre ESP32
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
db = DatabaseManager()
esp32_client = Client(ip=IP_ESP32)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        user = db.login(name, password)
        if user:
            session['user_id'] = user[0]
            session['role'] = user[3]
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Identifiants invalides"), 401
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.get_user_by_id(session['user_id'])
    user_list = db.get_users_list() if user[3] == 'admin' else []
    if user[3] == 'admin':
        try:
            communication_status = esp32_client._send_command(b"PING")
            if communication_status == b"PONG":
                communication_status_str = "Connecté"
            else:
                communication_status_str = "Non connecté"
        except WifiPacketError:
            communication_status_str = "Connexion impossible"
    else:
        communication_status_str = "Non autorisé"
    try:
        door_status_ = esp32_client._send_command(b"STATUS")
        print("door_status_:", door_status_)
        if door_status_ == b"OPEN":
            door_status_str = "Ouverte"
        elif door_status_ == b"CLOSED":
            door_status_str = "Fermée"
        else:
            door_status_str = "Inconnue"
    except WifiPacketError:
        door_status_str = "Connexion impossible"
    return render_template('home.html', name=user[1], role=user[3], users=user_list, door_status=door_status_str, communication_status=communication_status_str)

@app.route('/add_user', methods=['POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        role = request.form['role']
        success = db.add_user(name, password, role)
        if success:
            return redirect(url_for('home'))
        else:
            user = db.get_user_by_id(session['user_id'])
            user_list = db.get_users_list()
            return render_template(
                'home.html',
                name=user[1],
                role=user[3],
                users=user_list,
                error="Cet identifiant existe déjà. Choisissez un autre identifiant."
            ), 400
    return render_template('home.html')

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        role = request.form['role']
        db.edit_user(user_id, name=name, password=password, role=role)
        return redirect(url_for('home'))
    user = db.get_user_by_id(user_id)
    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:user_id>')
@admin_required
def delete_user(user_id):
    db.delete_user(user_id)
    return redirect(url_for('home'))

@app.route('/open_door', methods=['POST'])
def open_door():
    action = request.form.get('action')
    if action == 'open':
        try:
            esp32_client._send_command(b"OPEN")
        except WifiPacketError:
            pass
        return redirect(url_for('home'))
    else:
        return "Invalid action", 400

@app.route('/close_door', methods=['POST'])
def close_door():
    action = request.form.get('action')
    if action == 'close':
        try:
            esp32_client._send_command(b"CLOSE")
        except WifiPacketError:
            pass
        return redirect(url_for('home'))
    else:
        return "Invalid action", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
