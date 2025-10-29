from flask import Flask, render_template, request, redirect, session
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# ------------------------
# 🔹 Database connection helper
# ------------------------
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="employee_db",
        user="postgres",
        password="123"  # change this if needed
    )

#dkjdf
# ------------------------
# 🔸 LOGIN ROUTES
# ------------------------
@app.route('/')
def home():
    if 'user' in session:
        if session['role'] == 'admin':
            return redirect('/admin/dashboard')
        else:
            return redirect('/customer/dashboard')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user:
            session['user'] = user['username']
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect('/admin/dashboard')
            else:
                return redirect('/customer/dashboard')
        else:
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ------------------------
# 👤 CUSTOMER DASHBOARD
# ------------------------
@app.route('/customer/dashboard')
def customer_dashboard():
    if 'user' not in session or session['role'] != 'customer':
        return redirect('/login')

    username = session['user']
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('customer_dashboard.html', user=user)


# ------------------------
# 🧑‍💼 ADMIN DASHBOARD ROUTES
# ------------------------
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user' not in session or session['role'] != 'admin':
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM users ORDER BY id ASC")
    users = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('admin_dashboard.html', users=users)


@app.route('/admin/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user' not in session or session['role'] != 'admin':
        return redirect('/login')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
            (username, password, role)
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect('/admin/dashboard')

    return render_template('add_user.html')


@app.route('/admin/edit_user/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    if 'user' not in session or session['role'] != 'admin':
        return redirect('/login')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        cur.execute(
            "UPDATE users SET username=%s, password=%s, role=%s WHERE id=%s",
            (username, password, role, id)
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
def delete_user(id):
    if 'user' not in session or session['role'] != 'admin':
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
