from flask import Flask, render_template, request, redirect, url_for, session
from database import DatabaseManager    

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
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error="Identifiants invalides"), 401
    return render_template('login.html')

@app.route('/home')
def home():
    if 'user_id' in session:
        name_ = str(db.get_user_by_id(session['user_id'])[1])
        users_list = db.get_users_list()
        return render_template('home.html', name=name_, users=users_list)
    else:
        return redirect(url_for('login'))

@app.route('/add_user', methods=['POST'])
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
def delete_user(user_id):
    db.delete_user(user_id)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
