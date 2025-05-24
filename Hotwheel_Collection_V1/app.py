from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

os.makedirs('database', exist_ok=True)
os.makedirs('static/uploads', exist_ok=True)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('database/hotwheels.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return User(*user) if user else None


def init_db():
    conn = sqlite3.connect('database/hotwheels.db')
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS cars (id INTEGER PRIMARY KEY, name TEXT, year TEXT, category TEXT, image TEXT, user_id INTEGER)")
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS favorites (id INTEGER PRIMARY KEY, user_id INTEGER, car_id INTEGER)")
    cursor.execute("PRAGMA table_info(cars)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'user_id' not in columns:
        cursor.execute("ALTER TABLE cars ADD COLUMN user_id INTEGER")
    if 'category' not in columns:
        cursor.execute("ALTER TABLE cars ADD COLUMN category TEXT")
    conn.commit()
    conn.close()


init_db()


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    conn = sqlite3.connect('database/hotwheels.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        year = request.form['year']
        category = request.form['category']
        image = request.files['image']
        filename = ''
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cursor.execute("INSERT INTO cars (name, year, category, image, user_id) VALUES (?, ?, ?, ?, ?)",
                       (name, year, category, filename, current_user.id))
        conn.commit()

    search = request.args.get('search', '')
    category_filter = request.args.get('category', '')
    query = "SELECT * FROM cars WHERE user_id = ?"
    params = [current_user.id]
    if search:
        query += " AND name LIKE ?"
        params.append(f"%{search}%")
    if category_filter:
        query += " AND category = ?"
        params.append(category_filter)

    cursor.execute(query, params)
    cars = cursor.fetchall()
    cursor.execute("SELECT cars.name, COUNT(favorites.car_id) FROM favorites JOIN cars ON cars.id = favorites.car_id GROUP BY favorites.car_id ORDER BY COUNT(favorites.car_id) DESC LIMIT 5")
    top_favorites = cursor.fetchall()
    conn.close()
    return render_template('index.html', cars=cars, top_favorites=top_favorites)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        conn = sqlite3.connect('database/hotwheels.db')
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "Username already exists."
        finally:
            conn.close()
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database/hotwheels.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[2], password):
            login_user(User(*user))
            return redirect(url_for('index'))
        else:
            return "Invalid credentials."
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_car(id):
    conn = sqlite3.connect('database/hotwheels.db')
    cursor = conn.cursor()
    if request.method == 'POST':
        name = request.form['name']
        year = request.form['year']
        category = request.form['category']
        cursor.execute("UPDATE cars SET name=?, year=?, category=? WHERE id=? AND user_id=?",
                       (name, year, category, id, current_user.id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    cursor.execute("SELECT * FROM cars WHERE id=? AND user_id=?",
                   (id, current_user.id))
    car = cursor.fetchone()
    conn.close()
    return render_template('edit.html', car=car)


@app.route('/delete/<int:id>')
@login_required
def delete_car(id):
    conn = sqlite3.connect('database/hotwheels.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cars WHERE id=? AND user_id=?",
                   (id, current_user.id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


@app.route('/favorite/<int:car_id>')
@login_required
def favorite(car_id):
    conn = sqlite3.connect('database/hotwheels.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM favorites WHERE user_id=? AND car_id=?", (current_user.id, car_id))
    favorite = cursor.fetchone()
    if favorite:
        cursor.execute(
            "DELETE FROM favorites WHERE user_id=? AND car_id=?", (current_user.id, car_id))
    else:
        cursor.execute(
            "INSERT INTO favorites (user_id, car_id) VALUES (?, ?)", (current_user.id, car_id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
