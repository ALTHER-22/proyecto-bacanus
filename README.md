# 🎬 Bacanus - Sitio Web de Streaming

Sitio web para ver tu serie "Bacanus", creado con Flask + Python.

## ▶️ Cómo correr el proyecto

### 1. Abrir en PyCharm
- File → Open → selecciona la carpeta `proyecto_Bacanus`

### 2. Crear entorno virtual (como en tu otro proyecto)
- PyCharm lo sugiere automáticamente, acepta.
- O en terminal: `python -m venv .venv`

### 3. Instalar Flask
En la terminal de PyCharm:
```
pip install flask
```

### 4. Correr la app
```
python app.py
```

### 5. Abrir en el navegador
Ve a: http://127.0.0.1:5000

---

## 📁 Estructura del proyecto

```
proyecto_Bacanus/
├── app.py              ← Lógica principal (rutas)
├── requirements.txt    ← Dependencias
├── instance/
│   └── bacanus.db      ← Base de datos (se crea automáticamente)
├── static/
│   └── css/
│       └── styles.css  ← Diseño visual
└── templates/
    ├── base.html       ← Plantilla base (navbar, footer)
    ├── index.html      ← Página principal
    ├── episodio.html   ← Reproductor de video
    ├── admin.html      ← Panel de administración
    └── agregar.html    ← Formulario para agregar episodios
```

---

## 🎬 Cómo agregar tus episodios

Ve a: http://127.0.0.1:5000/admin → "Agregar Episodio"

### Si tu video está en YouTube:
1. Sube el video a YouTube
2. En la URL del video (ej: youtube.com/watch?v=ABC123)
3. Cámbiala a: https://www.youtube.com/embed/ABC123
4. Pega esa URL en el campo "URL de YouTube"

### Si tienes el archivo MP4:
- Pega la URL directa al archivo en "URL de video MP4"
- O puedes subir el archivo a Bunny.net o cualquier servidor

---

## 🌐 Para publicarlo en internet
Ver los pasos explicados en la conversación con Claude.
