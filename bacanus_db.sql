-- =============================================
-- BASE DE DATOS: proyecto_bacanus
-- Ejecutar en phpMyAdmin de XAMPP
-- =============================================

CREATE DATABASE IF NOT EXISTS proyecto_bacanus;
USE proyecto_bacanus;

CREATE TABLE IF NOT EXISTS episodios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    numero INT NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    url_youtube VARCHAR(500),
    url_mp4 VARCHAR(500),
    miniatura VARCHAR(500),
    duracion VARCHAR(20)
);

-- Episodios de ejemplo (puedes eliminarlos después)
INSERT INTO episodios (numero, titulo, descripcion, url_youtube, url_mp4, miniatura, duracion) VALUES
(1, 'El Comienzo', 'El inicio de la aventura de Bacanus en un mundo desconocido.', 'https://www.youtube.com/embed/dQw4w9WgXcQ', NULL, NULL, '24:00'),
(2, 'La Sombra', 'Bacanus descubre una amenaza oculta que cambiará su destino.', 'https://www.youtube.com/embed/dQw4w9WgXcQ', NULL, NULL, '23:45'),
(3, 'El Despertar', 'Un nuevo poder surge en el momento más inesperado.', 'https://www.youtube.com/embed/dQw4w9WgXcQ', NULL, NULL, '25:10');
