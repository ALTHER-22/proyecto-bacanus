from flask import Flask, render_template, request, redirect
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bacanus.db')

# ===============================
# CONEXIÓN
# ===============================
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS episodios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            url_youtube TEXT,
            url_mp4 TEXT,
            miniatura TEXT,
            duracion TEXT
        )
    ''')
    conn.commit()
    conn.close()

# ===============================
# RUTA PRINCIPAL
# ===============================
@app.route("/")
def index():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM episodios ORDER BY numero ASC")
    episodios = cursor.fetchall()
    conn.close()
    return render_template("index.html", episodios=episodios)

# ===============================
# VER EPISODIO
# ===============================
@app.route("/episodio/<int:id>")
def ver_episodio(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM episodios WHERE id = ?", (id,))
    episodio = cursor.fetchone()
    cursor.execute("SELECT * FROM episodios ORDER BY numero ASC")
    todos = cursor.fetchall()
    conn.close()
    if episodio is None:
        return redirect("/")
    return render_template("episodio.html", episodio=episodio, todos=todos)

# ===============================
# ADMIN - VER EPISODIOS
# ===============================
@app.route("/admin")
def admin():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM episodios ORDER BY numero ASC")
    episodios = cursor.fetchall()
    conn.close()
    return render_template("admin.html", episodios=episodios)

# ===============================
# ADMIN - AGREGAR EPISODIO
# ===============================
@app.route("/admin/agregar", methods=["GET", "POST"])
def agregar_episodio():
    if request.method == "POST":
        numero = request.form["numero"]
        titulo = request.form["titulo"]
        descripcion = request.form["descripcion"]
        url_youtube = request.form["url_youtube"]
        url_mp4 = request.form["url_mp4"]
        miniatura = request.form["miniatura"]
        duracion = request.form["duracion"]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO episodios (numero, titulo, descripcion, url_youtube, url_mp4, miniatura, duracion) VALUES (?,?,?,?,?,?,?)",
            (numero, titulo, descripcion, url_youtube, url_mp4, miniatura, duracion)
        )
        conn.commit()
        conn.close()
        return redirect("/admin")
    return render_template("agregar.html")

# ===============================
# ADMIN - EDITAR EPISODIO
# ===============================
@app.route("/admin/editar/<int:id>", methods=["GET", "POST"])
def editar_episodio(id):
    conn = get_connection()
    cursor = conn.cursor()
    if request.method == "POST":
        numero = request.form["numero"]
        titulo = request.form["titulo"]
        descripcion = request.form["descripcion"]
        url_youtube = request.form["url_youtube"]
        url_mp4 = request.form["url_mp4"]
        miniatura = request.form["miniatura"]
        duracion = request.form["duracion"]
        cursor.execute(
            "UPDATE episodios SET numero=?, titulo=?, descripcion=?, url_youtube=?, url_mp4=?, miniatura=?, duracion=? WHERE id=?",
            (numero, titulo, descripcion, url_youtube, url_mp4, miniatura, duracion, id)
        )
        conn.commit()
        conn.close()
        return redirect("/admin")
    cursor.execute("SELECT * FROM episodios WHERE id = ?", (id,))
    episodio = cursor.fetchone()
    conn.close()
    return render_template("editar.html", episodio=episodio)

# ===============================
# ADMIN - ELIMINAR EPISODIO
# ===============================
@app.route("/admin/eliminar/<int:id>")
def eliminar_episodio(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM episodios WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/admin")

# ===============================
# INICIAR
# ===============================
init_db()

if __name__ == "__main__":
    app.run(debug=True)