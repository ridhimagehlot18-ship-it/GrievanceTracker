from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'grievance_hackathon_2026_secret'

# Database Setup
def init_db():
    conn = sqlite3.connect('complaints.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS complaints
        (id TEXT PRIMARY KEY, category TEXT, location TEXT, description TEXT, 
         status TEXT DEFAULT 'Submitted', created_at TEXT, updated_at TEXT)''')
    conn.execute('''CREATE TABLE IF NOT EXISTS admin_users
        (username TEXT PRIMARY KEY, password TEXT)''')
    # Demo admin user
    conn.execute("INSERT OR IGNORE INTO admin_users VALUES ('admin', 'admin123')")
    conn.commit()
    conn.close()

init_db()

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        category = request.form['category']
        location = request.form['location']
        description = request.form['description']
        
        complaint_id = 'CMP' + str(uuid.uuid4().hex[:6]).upper()
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        conn = sqlite3.connect('complaints.db')
        conn.execute("INSERT INTO complaints VALUES (?, ?, ?, ?, 'Submitted', ?, ?)",
                    (complaint_id, category, location, description, now, now))
        conn.commit()
        conn.close()
        
        flash(f'✅ Success! Your Complaint ID: <strong>{complaint_id}</strong><br>Save this to track status.', 'success')
        return redirect('/track')
    
    return render_template('submit.html')

@app.route('/track', methods=['GET', 'POST'])
def track():
    complaint = None
    if request.method == 'POST':
        id = request.form['id'].upper().strip()
        conn = sqlite3.connect('complaints.db')
        complaint = conn.execute("SELECT * FROM complaints WHERE id=?", (id,)).fetchone()
        conn.close()
        if not complaint:
            flash('❌ Complaint ID not found!', 'danger')
    
    return render_template('track.html', complaint=complaint)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('complaints.db')
        user = conn.execute("SELECT * FROM admin_users WHERE username=? AND password=?", 
                           (username, password)).fetchone()
        conn.close()
        
        if user:
            session['admin'] = True
            return redirect('/admin')
        flash('❌ Wrong credentials! Demo: admin/admin123', 'danger')
    
    return render_template('admin_login.html')

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/admin_login')
    
    conn = sqlite3.connect('complaints.db')
    complaints = conn.execute("SELECT * FROM complaints ORDER BY created_at DESC").fetchall()
    conn.close()
    
    return render_template('admin.html', complaints=complaints)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    flash('Logged out', 'info')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
