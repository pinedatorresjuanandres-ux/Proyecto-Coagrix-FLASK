-- CoAgrix Database Schema
-- For XAMPP (phpMyAdmin)

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

-- --------------------------------------------------------

--
-- Table structure for table `roles`
--

CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `roles` (`id`, `nombre`) VALUES
(1, 'Administrador'),
(2, 'Campesino'),
(3, 'Empresa'),
(4, 'Comerciante');

-- --------------------------------------------------------

--
-- Table structure for table `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL UNIQUE,
  `password` varchar(255) NOT NULL, -- Stored in plain text as requested
  `reset_token` varchar(255) DEFAULT NULL,
  `reset_token_expira` datetime DEFAULT NULL,
  `rol_id` int(11) NOT NULL,
  `estado` enum('Activo','Inactivo') DEFAULT 'Activo',
  `fecha_registro` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_reset_token` (`reset_token`),
  FOREIGN KEY (`rol_id`) REFERENCES `roles`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `ubicaciones`
--

CREATE TABLE `ubicaciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `departamento` varchar(100) NOT NULL,
  `municipio` varchar(100) NOT NULL,
  `direccion` varchar(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `campesinos`
--

CREATE TABLE `campesinos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `telefono` varchar(20),
  `foto_perfil` varchar(255),
  `ubicacion_id` int(11),
  `descripcion` text,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`ubicacion_id`) REFERENCES `ubicaciones`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `empresas`
--

CREATE TABLE `empresas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `nit` varchar(20),
  `telefono` varchar(20),
  `ubicacion_id` int(11),
  `sector` varchar(100),
  PRIMARY KEY (`id`),
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`ubicacion_id`) REFERENCES `ubicaciones`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `comerciantes`
--

CREATE TABLE `comerciantes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `telefono` varchar(20),
  `ubicacion_id` int(11),
  PRIMARY KEY (`id`),
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`ubicacion_id`) REFERENCES `ubicaciones`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `categorias`
--

CREATE TABLE `categorias` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_categoria_nombre` (`nombre`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `categorias` (`nombre`) VALUES
('Frutas'), ('Verduras'), ('Hortalizas'), ('Tubérculos'), ('Legumbres'),
('Cereales'), ('Café'), ('Cacao'), ('Flores'), ('Plantas'),
('Aromáticas'), ('Frutos secos'), ('Lácteos'), ('Huevos'), ('Carnes'),
('Miel'), ('Pescados'), ('Semillas'), ('Especias'), ('Abonos Orgánicos'),
('Fertilizantes'), ('Insumos Agrícolas'), ('Otros');

-- --------------------------------------------------------

--
-- Table structure for table `productos`
--

CREATE TABLE `productos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `categoria_id` int(11),
  `descripcion` text,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`categoria_id`) REFERENCES `categorias`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `cultivos`
--

CREATE TABLE `cultivos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `campesino_id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `area` float,
  `fecha_siembra` date,
  `estado` varchar(50),
  PRIMARY KEY (`id`),
  FOREIGN KEY (`campesino_id`) REFERENCES `campesinos`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `publicaciones`
--

CREATE TABLE `publicaciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `campesino_id` int(11) NOT NULL,
  `producto_id` int(11) NOT NULL,
  `titulo` varchar(255) NOT NULL,
  `descripcion` text,
  `precio` decimal(10,2) NOT NULL,
  `cantidad_disponible` float NOT NULL,
  `unidad_medida` varchar(20),
  `imagen` varchar(255) DEFAULT NULL,
  `transporte` tinyint(1) NOT NULL DEFAULT 0,
  `fecha_publicacion` timestamp DEFAULT CURRENT_TIMESTAMP,
  `estado` enum('Activa','Inactiva','Agotada') DEFAULT 'Activa',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`campesino_id`) REFERENCES `campesinos`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`producto_id`) REFERENCES `productos`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `archivos`
--

CREATE TABLE `archivos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `publicacion_id` int(11) NOT NULL,
  `ruta` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`publicacion_id`) REFERENCES `publicaciones`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `pedidos`
--

CREATE TABLE `pedidos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL, -- Comprador (Empresa o Comerciante)
  `fecha_pedido` timestamp DEFAULT CURRENT_TIMESTAMP,
  `estado` enum('Pendiente','Aceptado','Rechazado','Completado') DEFAULT 'Pendiente',
  `total` decimal(10,2),
  PRIMARY KEY (`id`),
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `detalle_pedidos`
--

CREATE TABLE `detalle_pedidos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pedido_id` int(11) NOT NULL,
  `publicacion_id` int(11) NOT NULL,
  `cantidad` float NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`pedido_id`) REFERENCES `pedidos`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`publicacion_id`) REFERENCES `publicaciones`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `solicitudes`
--

CREATE TABLE `solicitudes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `empresa_id` int(11) NOT NULL,
  `campesino_id` int(11) NOT NULL,
  `mensaje` text,
  `fecha` timestamp DEFAULT CURRENT_TIMESTAMP,
  `estado` enum('Pendiente','Respondida') DEFAULT 'Pendiente',
  PRIMARY KEY (`id`),
  FOREIGN KEY (`empresa_id`) REFERENCES `empresas`(`id`),
  FOREIGN KEY (`campesino_id`) REFERENCES `campesinos`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `mensajes`
--

CREATE TABLE `mensajes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `remitente_id` int(11) NOT NULL,
  `destinatario_id` int(11) NOT NULL,
  `contenido` text NOT NULL,
  `fecha` timestamp DEFAULT CURRENT_TIMESTAMP,
  `leido` boolean DEFAULT false,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`remitente_id`) REFERENCES `usuarios`(`id`),
  FOREIGN KEY (`destinatario_id`) REFERENCES `usuarios`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `notificaciones`
--

CREATE TABLE `notificaciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `mensaje` text NOT NULL,
  `fecha` timestamp DEFAULT CURRENT_TIMESTAMP,
  `leida` boolean DEFAULT false,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `favoritos`
--

CREATE TABLE `favoritos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `publicacion_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios`(`id`),
  FOREIGN KEY (`publicacion_id`) REFERENCES `publicaciones`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `reseñas`
--

CREATE TABLE `reseñas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `publicacion_id` int(11) NOT NULL,
  `calificacion` int(1) CHECK (`calificacion` BETWEEN 1 AND 5),
  `comentario` text,
  `fecha` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios`(`id`),
  FOREIGN KEY (`publicacion_id`) REFERENCES `publicaciones`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `historial`
--

CREATE TABLE `historial` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `accion` varchar(255) NOT NULL,
  `fecha` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`usuario_id`) REFERENCES `usuarios`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `historial_precios`
--

CREATE TABLE `historial_precios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `publicacion_id` int(11) NOT NULL,
  `precio_anterior` decimal(10,2) NOT NULL,
  `precio_nuevo` decimal(10,2) NOT NULL,
  `fecha_cambio` timestamp DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_publicacion` (`publicacion_id`),
  FOREIGN KEY (`publicacion_id`) REFERENCES `publicaciones`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Test Data
--

INSERT INTO `usuarios` (`nombre`, `email`, `password`, `rol_id`, `estado`) VALUES
('Admin CoAgrix', 'admin@coagrix.com', 'admin123', 1, 'Activo'),
('Juan Campesino', 'campesino@coagrix.com', 'campesino123', 2, 'Activo'),
('AgroExport S.A.S', 'empresa@coagrix.com', 'empresa123', 3, 'Activo'),
('Pedro Comerciante', 'comerciante@coagrix.com', 'comerciante123', 4, 'Activo');

INSERT INTO `ubicaciones` (`departamento`, `municipio`, `direccion`) VALUES
('Huila', 'Neiva', 'Vereda El Triunfo'),
('Cundinamarca', 'Bogotá', 'Calle 100 #15-20'),
('Antioquia', 'Medellín', 'Carrera 45 #30-10');

INSERT INTO `campesinos` (`usuario_id`, `telefono`, `ubicacion_id`, `descripcion`) VALUES
(2, '3101234567', 1, 'Productor de café y frutas orgánicas.');

INSERT INTO `empresas` (`usuario_id`, `nit`, `telefono`, `ubicacion_id`, `sector`) VALUES
(3, '900123456-7', '3209876543', 2, 'Exportación');

INSERT INTO `comerciantes` (`usuario_id`, `telefono`, `ubicacion_id`) VALUES
(4, '3155554433', 3);

INSERT INTO `productos` (`nombre`, `categoria_id`, `descripcion`) VALUES
('Café Especial', 3, 'Café de altura, secado al sol.'),
('Manzana Roja', 1, 'Manzanas frescas del Huila.'),
('Papa Criolla', 5, 'Papa de excelente calidad.');

INSERT INTO `cultivos` (`campesino_id`, `nombre`, `area`, `fecha_siembra`, `estado`) VALUES
(1, 'Cafetal Norte', 2.5, '2025-01-15', 'En Crecimiento');

INSERT INTO `publicaciones` (`campesino_id`, `producto_id`, `titulo`, `descripcion`, `precio`, `cantidad_disponible`, `unidad_medida`, `estado`) VALUES
(1, 1, 'Café de Origen Huila', 'Venta de café pergamino seco.', 15000.00, 500, 'kg', 'Activa'),
(1, 2, 'Manzanas Orgánicas', 'Cosecha fresca de temporada.', 5000.00, 100, 'kg', 'Activa');

COMMIT;
