-- =========================================================
-- CoAgrix - Migración: "Olvidé mi contraseña"
-- =========================================================
-- Este script es seguro de ejecutar sobre una base de datos
-- CoAgrix ya existente (no borra ni modifica datos actuales).
-- Requiere MySQL 8.0+ / MariaDB 10.5+ por el uso de
-- "IF NOT EXISTS" en ALTER TABLE ... ADD COLUMN.
-- =========================================================

-- Columnas nuevas en `usuarios` para el token de recuperación
-- de contraseña y su fecha de expiración.
ALTER TABLE `usuarios`
    ADD COLUMN IF NOT EXISTS `reset_token` varchar(255) DEFAULT NULL AFTER `password`,
    ADD COLUMN IF NOT EXISTS `reset_token_expira` datetime DEFAULT NULL AFTER `reset_token`;

-- Índice para que la búsqueda por token (al hacer clic en el enlace del
-- correo) sea rápida.
ALTER TABLE `usuarios`
    ADD INDEX IF NOT EXISTS `idx_reset_token` (`reset_token`);
