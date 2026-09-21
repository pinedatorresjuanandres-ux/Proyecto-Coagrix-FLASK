-- Migración: Historial de precios por publicación
-- Guarda cada cambio de precio de una publicación para poder comparar
-- cómo ha evolucionado el precio de un mismo producto entre varios
-- vendedores (usado en el panel del comerciante).
--
-- Ejecuta este script en phpMyAdmin (o `mysql -u root -p coagrix < sql/migracion_historial_precios.sql`)
-- si ya tenías la base de datos creada antes de este cambio.

CREATE TABLE IF NOT EXISTS `historial_precios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `publicacion_id` int(11) NOT NULL,
  `precio_anterior` decimal(10,2) NOT NULL,
  `precio_nuevo` decimal(10,2) NOT NULL,
  `fecha_cambio` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_publicacion` (`publicacion_id`),
  FOREIGN KEY (`publicacion_id`) REFERENCES `publicaciones`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Deja un registro inicial para cada publicación que ya exista, tomando su
-- precio actual como punto de partida del historial.
INSERT INTO `historial_precios` (`publicacion_id`, `precio_anterior`, `precio_nuevo`, `fecha_cambio`)
SELECT `id`, `precio`, `precio`, `fecha_publicacion`
FROM `publicaciones`
WHERE `id` NOT IN (SELECT DISTINCT `publicacion_id` FROM `historial_precios`);
