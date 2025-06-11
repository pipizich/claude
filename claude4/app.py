from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'art_gallery_secret_key'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS artworks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT NOT NULL,
        image_path TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    # Changed order to ASC so newer images appear on the right
    artworks = conn.execute('SELECT * FROM artworks ORDER BY created_at ASC').fetchall()
    conn.close()
    return render_template('index.html', artworks=artworks)

@app.route('/add', methods=['POST'])
def add_artwork():
    if 'image' not in request.files:
        flash('No image part')
        return redirect(url_for('index'))
    
    file = request.files['image']
    
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        # Generate unique filename
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4()}.{ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save the file
        file.save(file_path)
        
        # Save to database
        title = request.form.get('title', '')  # Optional title
        description = request.form['description']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO artworks (title, description, image_path) VALUES (?, ?, ?)',
                    (title, description, f"static/uploads/{unique_filename}"))
        conn.commit()
        conn.close()
        
        flash('Artwork added successfully')
        return redirect(url_for('index'))
    
    flash('Invalid file type')
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['POST'])
def edit_artwork(id):
    title = request.form.get('title', '')  # Optional title
    description = request.form['description']
    
    conn = get_db_connection()
    artwork = conn.execute('SELECT * FROM artworks WHERE id = ?', (id,)).fetchone()
    
    # Check if a new image was uploaded
    if 'image' in request.files and request.files['image'].filename != '':
        file = request.files['image']
        
        if allowed_file(file.filename):
            # Generate unique filename
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save the file
            file.save(file_path)
            
            # Remove old image if it exists
            old_image_path = artwork['image_path']
            if old_image_path.startswith('static/uploads/') and os.path.exists(old_image_path):
                try:
                    os.remove(old_image_path)
                except:
                    pass
            
            # Update database with new image
            conn.execute('UPDATE artworks SET title = ?, description = ?, image_path = ? WHERE id = ?',
                       (title, description, f"static/uploads/{unique_filename}", id))
        else:
            flash('Invalid file type')
            return redirect(url_for('index'))
    else:
        # Update database without changing the image
        conn.execute('UPDATE artworks SET title = ?, description = ? WHERE id = ?',
                   (title, description, id))
    
    conn.commit()
    conn.close()
    flash('Artwork updated successfully')
    return redirect(url_for('index'))

@app.route('/delete/<int:id>', methods=['POST'])
def delete_artwork(id):
    conn = get_db_connection()
    artwork = conn.execute('SELECT * FROM artworks WHERE id = ?', (id,)).fetchone()
    
    # Delete the image file if it exists
    image_path = artwork['image_path']
    if image_path.startswith('static/uploads/') and os.path.exists(image_path):
        try:
            os.remove(image_path)
        except:
            pass
    
    # Delete from database
    conn.execute('DELETE FROM artworks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    
    flash('Artwork deleted successfully')
    return redirect(url_for('index'))

@app.route('/get_description/<int:id>')
def get_description(id):
    conn = get_db_connection()
    artwork = conn.execute('SELECT title, description FROM artworks WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if artwork:
        return jsonify({
            'title': artwork['title'],
            'description': artwork['description']
        })
    return jsonify({'error': 'Artwork not found'}), 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)