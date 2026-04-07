from flask import Flask, render_template, request, redirect, session
import sqlite3, os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'bacanus_clave_secreta_2026'

ADMIN_USUARIO = 'bacanus'
ADMIN_PASSWORD = 'tuclave123'

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
        if request.form['usuario'] == ADMIN_USUARIO and request.form['password'] == ADMIN_PASSWORD:
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
    c = conn.cursor()
    c.execute("SELECT * FROM series WHERE categoria='serie' ORDER BY orden ASC, id ASC")
    series = c.fetchall()
    c.execute("SELECT * FROM series WHERE categoria='pelicula' ORDER BY orden ASC, id ASC")
    peliculas = c.fetchall()
    c.execute("SELECT * FROM series WHERE categoria='anime' ORDER BY orden ASC, id ASC")
    animes = c.fetchall()
    conn.close()
    return render_template('index.html', series=series, peliculas=peliculas, animes=animes)

@app.route('/series')
def ver_series():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM series WHERE categoria='serie' ORDER BY orden ASC, id ASC")
    series = c.fetchall()
    conn.close()
    return render_template('categoria.html', items=series, titulo='Series')

@app.route('/peliculas')
def ver_peliculas():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM series WHERE categoria='pelicula' ORDER BY orden ASC, id ASC")
    peliculas = c.fetchall()
    conn.close()
    return render_template('categoria.html', items=peliculas, titulo='Películas')

@app.route('/anime')
def ver_anime():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM series WHERE categoria='anime' ORDER BY orden ASC, id ASC")
    animes = c.fetchall()
    conn.close()
    return render_template('categoria.html', items=animes, titulo='Anime')

@app.route('/serie/<int:id>')
def ver_serie(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM series WHERE id = ?", (id,))
    serie = c.fetchone()
    if serie is None:
        return redirect('/')
    c.execute("SELECT * FROM episodios WHERE serie_id = ? ORDER BY numero ASC", (id,))
    episodios = c.fetchall()
    conn.close()
    return render_template('serie.html', serie=serie, episodios=episodios)

@app.route('/episodio/<int:id>')
def ver_episodio(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM episodios WHERE id = ?", (id,))
    episodio = c.fetchone()
    if episodio is None:
        return redirect('/')
    c.execute("SELECT * FROM series WHERE id = ?", (episodio['serie_id'],))
    serie = c.fetchone()
    c.execute("SELECT * FROM episodios WHERE serie_id = ? ORDER BY numero ASC", (episodio['serie_id'],))
    todos = c.fetchall()
    conn.close()
    return render_template('episodio.html', episodio=episodio, serie=serie, todos=todos)

@app.route('/admin')
@login_requerido
def admin():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM series ORDER BY categoria, orden ASC, id ASC")
    series = c.fetchall()
    conn.close()
    return render_template('admin.html', series=series)

@app.route('/admin/agregar-serie', methods=['GET', 'POST'])
@login_requerido
def agregar_serie():
    if request.method == 'POST':
        conn = get_connection()
        conn.cursor().execute("INSERT INTO series (titulo, descripcion, miniatura, orden, categoria) VALUES (?,?,?,?,?)",
            (request.form['titulo'], request.form['descripcion'], request.form['miniatura'], request.form.get('orden', 0), request.form.get('categoria', 'serie')))
        conn.commit(); conn.close()
        return redirect('/admin')
    return render_template('agregar_serie.html')

@app.route('/admin/editar-serie/<int:id>', methods=['GET', 'POST'])
@login_requerido
def editar_serie(id):
    conn = get_connection()
    c = conn.cursor()
    if request.method == 'POST':
        c.execute("UPDATE series SET titulo=?, descripcion=?, miniatura=?, orden=?, categoria=? WHERE id=?",
            (request.form['titulo'], request.form['descripcion'], request.form['miniatura'], request.form.get('orden', 0), request.form.get('categoria', 'serie'), id))
        conn.commit(); conn.close()
        return redirect('/admin')
    c.execute("SELECT * FROM series WHERE id = ?", (id,))
    serie = c.fetchone()
    conn.close()
    return render_template('editar_serie.html', serie=serie)

@app.route('/admin/eliminar-serie/<int:id>')
@login_requerido
def eliminar_serie(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM episodios WHERE serie_id = ?", (id,))
    c.execute("DELETE FROM series WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return redirect('/admin')

@app.route('/admin/serie/<int:serie_id>/episodios')
@login_requerido
def admin_episodios(serie_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM series WHERE id = ?", (serie_id,))
    serie = c.fetchone()
    c.execute("SELECT * FROM episodios WHERE serie_id = ? ORDER BY numero ASC", (serie_id,))
    episodios = c.fetchall()
    conn.close()
    return render_template('admin_episodios.html', serie=serie, episodios=episodios)

@app.route('/admin/serie/<int:serie_id>/agregar', methods=['GET', 'POST'])
@login_requerido
def agregar_episodio(serie_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM series WHERE id = ?", (serie_id,))
    serie = c.fetchone()
    if request.method == 'POST':
        c.execute("INSERT INTO episodios (serie_id, numero, titulo, descripcion, url_youtube, url_mp4, miniatura, duracion) VALUES (?,?,?,?,?,?,?,?)",
            (serie_id, request.form['numero'], request.form['titulo'], request.form['descripcion'],
             request.form['url_youtube'], request.form['url_mp4'], request.form['miniatura'], request.form['duracion']))
        conn.commit(); conn.close()
        return redirect(f'/admin/serie/{serie_id}/episodios')
    conn.close()
    return render_template('agregar.html', serie=serie)

@app.route('/admin/editar/<int:id>', methods=['GET', 'POST'])
@login_requerido
def editar_episodio(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM episodios WHERE id = ?", (id,))
    episodio = c.fetchone()
    c.execute("SELECT * FROM series WHERE id = ?", (episodio['serie_id'],))
    serie = c.fetchone()
    if request.method == 'POST':
        c.execute("UPDATE episodios SET numero=?, titulo=?, descripcion=?, url_youtube=?, url_mp4=?, miniatura=?, duracion=? WHERE id=?",
            (request.form['numero'], request.form['titulo'], request.form['descripcion'],
             request.form['url_youtube'], request.form['url_mp4'], request.form['miniatura'], request.form['duracion'], id))
        conn.commit(); conn.close()
        return redirect(f'/admin/serie/{serie["id"]}/episodios')
    conn.close()
    return render_template('editar.html', episodio=episodio, serie=serie)

@app.route('/admin/eliminar/<int:id>')
@login_requerido
def eliminar_episodio(id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT serie_id FROM episodios WHERE id = ?", (id,))
    serie_id = c.fetchone()['serie_id']
    c.execute("DELETE FROM episodios WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return redirect(f'/admin/serie/{serie_id}/episodios')

init_db()

if __name__ == '__main__':
    app.run(debug=True)
