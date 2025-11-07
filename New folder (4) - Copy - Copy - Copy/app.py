from flask import Flask, render_template, request, redirect, jsonify, make_response
import psycopg2
import psycopg2.extras
import jwt
import datetime
from functools import wraps
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
CORS(app, supports_credentials=True)

SECRET_KEY = "super_secret_jwt_key"


# ------------------------
# 🔹 Database connection helper
# ------------------------
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="employee_db",
        user="postgres",
        password="123"
    )


# ------------------------
# 🧱 JWT Decorator
# ------------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check both Cookie and Header for JWT
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        elif request.cookies.get('token'):
            token = request.cookies.get('token')

        if not token:
            return redirect('/login')

        try:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = decoded['username']
            role = decoded['role']

            # 👇 Print decoded info in your Flask terminal
            print("\n✅ JWT Decoded Info:")
            print(f"Username: {current_user}, Role: {role}, Exp: {decoded['exp']}")

        except jwt.ExpiredSignatureError:
            print("\n❌ Token expired.")
            return redirect('/login')
        except Exception as e:
            print(f"\n❌ Invalid token: {e}")
            return redirect('/login')

        return f(current_user, role, *args, **kwargs)
    return decorated


# ------------------------
# 🔒 Test Token Decode API
# ------------------------
@app.route('/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'error': 'Missing token'}), 401

    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        print("\n✅ DECODED TOKEN DATA:")
        print(decoded)
        return jsonify({'message': 'Access granted', 'decoded': decoded})
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401


# ------------------------
# 🔸 LOGIN ROUTES (JWT version)
# ------------------------
@app.route('/')
def home():
    token = request.cookies.get('token')
    if token:
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            if data['role'] == 'admin':
                return redirect('/admin/dashboard')
            else:
                return redirect('/customer/dashboard')
        except:
            return redirect('/login')
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username')
    password = request.form.get('password')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if not user:
        return render_template('login.html', error='Invalid username or password')

    token = jwt.encode({
        'username': user['username'],
        'role': user['role'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm="HS256")

    response = make_response(redirect('/admin/dashboard' if user['role'] == 'admin' else '/customer/dashboard'))
    response.set_cookie('token', token, httponly=True, samesite='Lax', secure=False)

    print("\n🎟️ Generated JWT Token:", token)
    return response


@app.route('/logout')
def logout():
    response = make_response(redirect('/login'))
    response.delete_cookie('token')
    return response


# ------------------------
# 👤 CUSTOMER DASHBOARD
# ------------------------
@app.route('/customer/dashboard')
@token_required
def customer_dashboard(current_user, role):
    if role != 'customer':
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM users WHERE username=%s", (current_user,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('customer_dashboard.html', user=user)


# ------------------------
# 🧑‍💼 ADMIN DASHBOARD ROUTES
# ------------------------
@app.route('/admin/dashboard')
@token_required
def admin_dashboard(current_user, role):
    if role != 'admin':
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM users ORDER BY id ASC")
    users = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('admin_dashboard.html', users=users)


@app.route('/admin/add_user', methods=['GET', 'POST'])
@token_required
def add_user(current_user, role):
    if role != 'admin':
        return redirect('/login')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_role = request.form['role']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, password, user_role)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect('/admin/dashboard')

    return render_template('add_user.html')


@app.route('/admin/edit_user/<int:id>', methods=['GET', 'POST'])
@token_required
def edit_user(current_user, role, id):
    if role != 'admin':
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_role = request.form['role']

        cur.execute(
            "UPDATE users SET username=%s, password=%s, role=%s WHERE id=%s",
            (username, password, user_role, id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/admin/dashboard')

    cur.execute("SELECT * FROM users WHERE id=%s", (id,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('edit_user.html', user=user)


@app.route('/admin/delete_user/<int:id>')
@token_required
def delete_user(current_user, role, id):
    if role != 'admin':
        return redirect('/login')
    
    

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect('/admin/dashboard')


# ------------------------
# 🚀 Run App
# ------------------------
if __name__ == '__main__':
    app.run(debug=True)
