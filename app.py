from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = os.urandom(24)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'BOOKBANK'

mysql = MySQL(app)

# Helper functions
def get_db_connection():
    return mysql.connection.cursor()

def close_db_connection(cursor):
    cursor.close()

def is_logged_in():
    return 'user_id' in session

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/catalog')
def catalog():
    return render_template('catalog.html')

@app.route('/exchange')
def exchange():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('exchange.html')

@app.route('/profile')
def profile():
    if not is_logged_in():
        return redirect(url_for('login'))
    return render_template('profile.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        cursor = get_db_connection()
        cursor.execute("SELECT * FROM USERS WHERE username = %s", (username,))
        user = cursor.fetchone()
        close_db_connection(cursor)
        
        if user and check_password_hash(user[3], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            return jsonify({'success': True, 'message': 'Login successful'})
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'})
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        cursor = get_db_connection()
        try:
            cursor.execute("INSERT INTO USERS (username, email, password) VALUES (%s, %s, %s)",
                           (username, email, hashed_password))
            mysql.connection.commit()
            return jsonify({'success': True, 'message': 'Registration successful'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
        finally:
            close_db_connection(cursor)
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# API routes
@app.route('/api/books', methods=['GET'])
def get_books():
    cursor = get_db_connection()
    cursor.execute("SELECT * FROM BOOKS")
    books = cursor.fetchall()
    close_db_connection(cursor)
    return jsonify(books)

@app.route('/api/books/search', methods=['GET'])
def search_books():
    query = request.args.get('q', '')
    cursor = get_db_connection()
    cursor.execute("SELECT * FROM BOOKS WHERE title LIKE %s OR author LIKE %s OR genre LIKE %s",
                   (f'%{query}%', f'%{query}%', f'%{query}%'))
    books = cursor.fetchall()
    close_db_connection(cursor)
    return jsonify(books)

@app.route('/api/books/reserve', methods=['POST'])
def reserve_book():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'User not logged in'})
    
    book_id = request.form.get('book_id')
    user_id = session['user_id']
    
    cursor = get_db_connection()
    try:
        cursor.execute("UPDATE BOOKS SET status = 'reserved' WHERE id = %s AND status = 'available'", (book_id,))
        if cursor.rowcount > 0:
            cursor.execute("INSERT INTO TRANSACTIONS (book_id, borrower_id, transaction_type) VALUES (%s, %s, 'borrow')",
                           (book_id, user_id))
            mysql.connection.commit()
            return jsonify({'success': True, 'message': 'Book reserved successfully'})
        else:
            return jsonify({'success': False, 'message': 'Book not available for reservation'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        close_db_connection(cursor)

@app.route('/api/books/exchange', methods=['POST'])
def exchange_book():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'User not logged in'})
    
    book_id = request.form.get('book_id')
    user_id = session['user_id']
    
    cursor = get_db_connection()
    try:
        cursor.execute("SELECT owner_id, status FROM BOOKS WHERE id = %s", (book_id,))
        book = cursor.fetchone()
        if not book or book[1] != 'available':
            return jsonify({'success': False, 'message': 'Book not available for exchange'})
        
        owner_id = book[0]
        if owner_id == user_id:
            return jsonify({'success': False, 'message': 'You cannot exchange your own book'})
        
        cursor.execute("UPDATE BOOKS SET owner_id = %s WHERE id = %s", (user_id, book_id))
        cursor.execute("INSERT INTO TRANSACTIONS (book_id, borrower_id, lender_id, transaction_type) VALUES (%s, %s, %s, 'exchange')",
                       (book_id, user_id, owner_id))
        cursor.execute("UPDATE USERS SET points = points + 1 WHERE id = %s", (user_id,))
        mysql.connection.commit()
        return jsonify({'success': True, 'message': 'Book exchanged successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        close_db_connection(cursor)

@app.route('/api/recommendations', methods=['GET'])
def get_recommendations():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'User not logged in'})
    
    user_id = session['user_id']
    cursor = get_db_connection()
    try:
        # Get user's reading history
        cursor.execute("""
            SELECT DISTINCT b.genre
            FROM TRANSACTIONS t
            JOIN BOOKS b ON t.book_id = b.id
            WHERE t.borrower_id = %s
            ORDER BY t.transaction_date DESC
            LIMIT 5
        """, (user_id,))
        user_genres = [row[0] for row in cursor.fetchall()]
        
        # Get recommendations based on user's reading history
        recommendations = []
        for genre in user_genres:
            cursor.execute("""
                SELECT b.*
                FROM BOOKS b
                LEFT JOIN TRANSACTIONS t ON b.id = t.book_id AND t.borrower_id = %s
                WHERE b.genre = %s AND t.id IS NULL
                LIMIT 2
            """, (user_id, genre))
            recommendations.extend(cursor.fetchall())
        
        return jsonify({'success': True, 'recommendations': recommendations})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        close_db_connection(cursor)

@app.route('/api/user/points', methods=['GET'])
def get_user_points():
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'User not logged in'})
    
    user_id = session['user_id']
    cursor = get_db_connection()
    try:
        cursor.execute("SELECT points FROM USERS WHERE id = %s", (user_id,))
        points = cursor.fetchone()[0]
        return jsonify({'success': True, 'points': points})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        close_db_connection(cursor)

if __name__ == '__main__':
    app.run(debug=True)