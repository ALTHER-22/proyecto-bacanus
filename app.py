from flask import Flask, render_template, request, redirect, session
import sqlite3, os
from functools import wraps
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
# Mejorar seguridad con variables de entorno para la clave secreta
app.secret_key = os.environ.get('SECRET_KEY', 'bacanus_clave_secreta_2026')
csrf = CSRFProtect(app)

# Configuración segura para la sesión (evita ataques XSS/CSRF básicos)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800,  # 30 minutos de inactividad
    SEND_FILE_MAX_AGE_DEFAULT=43200,  # Caché de archivos estáticos: 12 horas
)

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    return response  # BUG CRÍTICO CORREGIDO: faltaba este return

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bacanus.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS series (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT NOT NULL, descripcion TEXT, miniatura TEXT, orden INTEGER DEFAULT 0, categoria TEXT DEFAULT "serie")''')
    c.execute('''CREATE TABLE IF NOT EXISTS episodios (id INTEGER PRIMARY KEY AUTOINCREMENT, serie_id INTEGER NOT NULL, numero INTEGER NOT NULL, titulo TEXT NOT NULL, descripcion TEXT, url_youtube TEXT, url_mp4 TEXT, miniatura TEXT, duracion TEXT, FOREIGN KEY (serie_id) REFERENCES series(id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL)''')
    
    # Crear administrador por defecto si no existen usuarios
    c.execute("SELECT COUNT(*) FROM usuarios")
    if c.fetchone()[0] == 0:
        admin_user = os.environ.get('ADMIN_USUARIO', 'admin')
        admin_pass = os.environ.get('ADMIN_PASSWORD', 'admin123')
        admin_hash = generate_password_hash(admin_pass)
        c.execute("INSERT INTO usuarios (username, password_hash) VALUES (?, ?)", (admin_user, admin_hash))

    # Crear índices para mejorar la velocidad y rendimiento de las consultas (performance)
    c.execute('CREATE INDEX IF NOT EXISTS idx_series_categoria_orden ON series (categoria, orden, id)')
    c.execute('CREATE INDEX IF NOT EXISTS idx_episodios_serie_numero ON episodios (serie_id, numero)')
    
    conn.commit()
    conn.close()

def login_requerido(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        if not session.get('admin'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorador

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        conn = get_connection()
        try:
            c = conn.cursor()
            c.execute("SELECT * FROM usuarios WHERE username = ?", (request.form['usuario'],))
            user = c.fetchone()
        finally:
            conn.close()
        
        if user and check_password_hash(user['password_hash'], request.form['password']):
            session.permanent = True  # Activar tiempo de expiración
            session['admin'] = True
            return redirect('/admin')
        else:
            error = 'Usuario o contraseña incorrectos'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

@app.route('/')
def index():
    conn = get_connection()
    try:
        c = conn.cursor()
        # Una sola consulta en vez de 3 separadas (más rápido)
        c.execute("SELECT * FROM series ORDER BY categoria, orden ASC, id ASC")
        todas = c.fetchall()
    finally:
        conn.close()
    series = [s for s in todas if s['categoria'] == 'serie']
    peliculas = [s for s in todas if s['categoria'] == 'pelicula']
    animes = [s for s in todas if s['categoria'] == 'anime']
    return render_template('index.html', series=series, peliculas=peliculas, animes=animes)

@app.route('/series')
def ver_series():
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM series WHERE categoria='serie' ORDER BY orden ASC, id ASC")
        series = c.fetchall()
    finally:
        conn.close()
    return render_template('categoria.html', items=series, titulo='Series')

@app.route('/peliculas')
def ver_peliculas():
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM series WHERE categoria='pelicula' ORDER BY orden ASC, id ASC")
        peliculas = c.fetchall()
    finally:
        conn.close()
    return render_template('categoria.html', items=peliculas, titulo='Películas')

@app.route('/anime')
def ver_anime():
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM series WHERE categoria='anime' ORDER BY orden ASC, id ASC")
        animes = c.fetchall()
    finally:
        conn.close()
    return render_template('categoria.html', items=animes, titulo='Anime')

@app.route('/serie/<int:id>')
def ver_serie(id):
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM series WHERE id = ?", (id,))
        serie = c.fetchone()
        if serie is None:
            return redirect('/')
        c.execute("SELECT * FROM episodios WHERE serie_id = ? ORDER BY numero ASC", (id,))
        episodios = c.fetchall()
    finally:
        conn.close()
    return render_template('serie.html', serie=serie, episodios=episodios)

@app.route('/episodio/<int:id>')
def ver_episodio(id):
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM episodios WHERE id = ?", (id,))
        episodio = c.fetchone()
        if episodio is None:
            return redirect('/')
        c.execute("SELECT * FROM series WHERE id = ?", (episodio['serie_id'],))
        serie = c.fetchone()
        c.execute("SELECT * FROM episodios WHERE serie_id = ? ORDER BY numero ASC", (episodio['serie_id'],))
        todos = c.fetchall()
    finally:
        conn.close()
    return render_template('episodio.html', episodio=episodio, serie=serie, todos=todos)

@app.route('/admin')
@login_requerido
def admin():
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM series ORDER BY categoria, orden ASC, id ASC")
        series = c.fetchall()
    finally:
        conn.close()
    return render_template('admin.html', series=series)

@app.route('/admin/agregar-serie', methods=['GET', 'POST'])
@login_requerido
def agregar_serie():
    if request.method == 'POST':
        titulo = request.form['titulo'].strip()
        if not titulo:
            return redirect('/admin')
        conn = get_connection()
        try:
            conn.cursor().execute("INSERT INTO series (titulo, descripcion, miniatura, orden, categoria) VALUES (?,?,?,?,?)",
                (titulo, request.form['descripcion'].strip(), request.form['miniatura'].strip(), request.form.get('orden', 0), request.form.get('categoria', 'serie')))
            conn.commit()
        finally:
            conn.close()
        return redirect('/admin')
    return render_template('agregar_serie.html')

@app.route('/admin/editar-serie/<int:id>', methods=['GET', 'POST'])
@login_requerido
def editar_serie(id):
    conn = get_connection()
    try:
        c = conn.cursor()
        if request.method == 'POST':
            c.execute("UPDATE series SET titulo=?, descripcion=?, miniatura=?, orden=?, categoria=? WHERE id=?",
                (request.form['titulo'].strip(), request.form['descripcion'].strip(), request.form['miniatura'].strip(), request.form.get('orden', 0), request.form.get('categoria', 'serie'), id))
            conn.commit()
            return redirect('/admin')
        c.execute("SELECT * FROM series WHERE id = ?", (id,))
        serie = c.fetchone()
    finally:
        conn.close()
    return render_template('editar_serie.html', serie=serie)

# Eliminar serie ahora requiere POST (protección contra ataques por enlace)
@app.route('/admin/eliminar-serie/<int:id>', methods=['POST'])
@login_requerido
def eliminar_serie(id):
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("DELETE FROM episodios WHERE serie_id = ?", (id,))
        c.execute("DELETE FROM series WHERE id = ?", (id,))
        conn.commit()
    finally:
        conn.close()
    return redirect('/admin')

@app.route('/admin/serie/<int:serie_id>/episodios')
@login_requerido
def admin_episodios(serie_id):
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM series WHERE id = ?", (serie_id,))
        serie = c.fetchone()
        c.execute("SELECT * FROM episodios WHERE serie_id = ? ORDER BY numero ASC", (serie_id,))
        episodios = c.fetchall()
    finally:
        conn.close()
    return render_template('admin_episodios.html', serie=serie, episodios=episodios)

@app.route('/admin/serie/<int:serie_id>/agregar', methods=['GET', 'POST'])
@login_requerido
def agregar_episodio(serie_id):
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM series WHERE id = ?", (serie_id,))
        serie = c.fetchone()
        if request.method == 'POST':
            c.execute("INSERT INTO episodios (serie_id, numero, titulo, descripcion, url_youtube, url_mp4, miniatura, duracion) VALUES (?,?,?,?,?,?,?,?)",
                (serie_id, request.form['numero'], request.form['titulo'].strip(), request.form['descripcion'].strip(),
                 request.form['url_youtube'].strip(), request.form['url_mp4'].strip(), request.form['miniatura'].strip(), request.form['duracion'].strip()))
            conn.commit()
            return redirect(f'/admin/serie/{serie_id}/episodios')
    finally:
        conn.close()
    return render_template('agregar.html', serie=serie)

@app.route('/admin/editar/<int:id>', methods=['GET', 'POST'])
@login_requerido
def editar_episodio(id):
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM episodios WHERE id = ?", (id,))
        episodio = c.fetchone()
        c.execute("SELECT * FROM series WHERE id = ?", (episodio['serie_id'],))
        serie = c.fetchone()
        if request.method == 'POST':
            c.execute("UPDATE episodios SET numero=?, titulo=?, descripcion=?, url_youtube=?, url_mp4=?, miniatura=?, duracion=? WHERE id=?",
                (request.form['numero'], request.form['titulo'].strip(), request.form['descripcion'].strip(),
                 request.form['url_youtube'].strip(), request.form['url_mp4'].strip(), request.form['miniatura'].strip(), request.form['duracion'].strip(), id))
            conn.commit()
            return redirect(f'/admin/serie/{serie["id"]}/episodios')
    finally:
        conn.close()
    return render_template('editar.html', episodio=episodio, serie=serie)

# Eliminar episodio ahora requiere POST (protección contra ataques por enlace)
@app.route('/admin/eliminar/<int:id>', methods=['POST'])
@login_requerido
def eliminar_episodio(id):
    conn = get_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT serie_id FROM episodios WHERE id = ?", (id,))
        serie_id = c.fetchone()['serie_id']
        c.execute("DELETE FROM episodios WHERE id = ?", (id,))
        conn.commit()
    finally:
        conn.close()
    return redirect(f'/admin/serie/{serie_id}/episodios')

init_db()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False') == 'True'
    app.run(debug=debug_mode)
