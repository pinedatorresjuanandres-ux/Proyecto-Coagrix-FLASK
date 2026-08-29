-- =========================================================
-- CoAgrix - Migración: módulo "Agregar Producto"
-- =========================================================
-- Este script es seguro de ejecutar sobre una base de datos
-- CoAgrix ya existente (no borra ni modifica datos actuales).
-- Requiere MySQL 8.0+ / MariaDB 10.5+ por el uso de
-- "IF NOT EXISTS" en ALTER TABLE ... ADD COLUMN.
-- =========================================================

-- 1) Nuevas columnas en `publicaciones` para imagen y transporte
ALTER TABLE `publicaciones`
    ADD COLUMN IF NOT EXISTS `imagen` varchar(255) DEFAULT NULL AFTER `unidad_medida`,
    ADD COLUMN IF NOT EXISTS `transporte` tinyint(1) NOT NULL DEFAULT 0 AFTER `imagen`;

-- 2) Restricción de unicidad en categorías (evita duplicados futuros)
--    Si ya existiera un índice con ese nombre, este ALTER fallará de forma
--    inofensiva; en ese caso puede omitirse esta línea.
ALTER TABLE `categorias`
    ADD UNIQUE KEY IF NOT EXISTS `uq_categoria_nombre` (`nombre`);

-- 3) Categorías agrícolas estándar (se ignoran las que ya existan)
INSERT IGNORE INTO `categorias` (`nombre`) VALUES
('Frutas'), ('Verduras'), ('Hortalizas'), ('Tubérculos'), ('Legumbres'),
('Cereales'), ('Café'), ('Cacao'), ('Flores'), ('Plantas'),
('Aromáticas'), ('Frutos secos'), ('Lácteos'), ('Huevos'), ('Carnes'),
('Miel'), ('Pescados'), ('Semillas'), ('Especias'), ('Abonos Orgánicos'),
('Fertilizantes'), ('Insumos Agrícolas'), ('Otros');
