from flask import Flask, render_template, request, redirect, url_for, session
from database import DatabaseManager
from functools import wraps
from flask import abort

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

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key
db = DatabaseManager()

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
    return render_template('home.html', name=user[1], role=user[3], users=user_list)

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
            return render_template('home.html', error="Erreur lors de l'ajout de l'utilisateur"), 400
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
