-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 21-09-2026 a las 18:21:59
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `coagrix2`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `archivos`
--

CREATE TABLE `archivos` (
  `id` int(11) NOT NULL,
  `publicacion_id` int(11) NOT NULL,
  `ruta` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `archivos`
--

INSERT INTO `archivos` (`id`, `publicacion_id`, `ruta`) VALUES
(34, 17, 'uploads/Rosas.jpg'),
(35, 14, 'uploads/Cafe_Pergamino.webp'),
(36, 15, 'uploads/Cafe_Tostado_Premium.webp'),
(37, 16, 'uploads/Cacao_en_Grano.jpg'),
(38, 11, 'uploads/Garbanzo.jpg'),
(39, 12, 'uploads/Maiz_Amarillo.png'),
(40, 13, 'uploads/Arroz_Blanco.webp'),
(41, 8, 'uploads/Papa_Pastusa.jpg'),
(42, 9, 'uploads/Yuca.jpg'),
(43, 10, 'uploads/Frijol_Cargamanto.png'),
(44, 7, 'uploads/Tomate_chonto.jpg'),
(45, 6, 'uploads/Zanahoria.png'),
(46, 5, 'uploads/Espinaca.jpg'),
(47, 4, 'uploads/Naranja_Valencia.jpg'),
(48, 3, 'uploads/Mango_Tommy.jpg'),
(49, 2, 'uploads/Manzana_Roja.jpg'),
(50, 32, 'uploads/Compost_Organico_para_Cultivos.jpg'),
(51, 29, 'uploads/Trucha_Arcoiris.jpeg'),
(52, 30, 'uploads/Semillas_de_Girasol.jpg'),
(53, 31, 'uploads/Pimienta_Negra.webp'),
(54, 26, 'uploads/Huevos_AA.jpg'),
(55, 27, 'uploads/Pollo.webp'),
(56, 28, 'uploads/Miel_de_Abejas.jpg'),
(57, 23, 'uploads/Nueces.jpg'),
(58, 24, 'uploads/Queso_Campesino.jpg'),
(59, 25, 'uploads/Leche_Fresca.jpg'),
(60, 20, 'uploads/Albahaca.jpg'),
(61, 21, 'uploads/Cilantro.jpg'),
(62, 22, 'uploads/Almendras.jpeg'),
(63, 18, 'uploads/Claveles.jpg'),
(64, 19, 'uploads/Suculentas.jpg'),
(95, 63, 'uploads/Manicomio_Bus_9_16.png'),
(96, 64, 'uploads/Procesion_Pagana_9_16.png');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `campesinos`
--

CREATE TABLE `campesinos` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `foto_perfil` varchar(255) DEFAULT NULL,
  `ubicacion_id` int(11) DEFAULT NULL,
  `descripcion` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `campesinos`
--

INSERT INTO `campesinos` (`id`, `usuario_id`, `telefono`, `foto_perfil`, `ubicacion_id`, `descripcion`) VALUES
(1, 2, '3101234567', NULL, 1, 'Productor de café y frutas orgánicas.'),
(2, 5, '3187654321', NULL, 4, 'Productora de hortalizas, lácteos y productos apícolas en el oriente antioqueño.'),
(3, 10, '3213260180', NULL, 8, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `categorias`
--

CREATE TABLE `categorias` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `categorias`
--

INSERT INTO `categorias` (`id`, `nombre`) VALUES
(20, 'Abonos Orgánicos'),
(11, 'Aromáticas'),
(8, 'Cacao'),
(7, 'Café'),
(15, 'Carnes'),
(6, 'Cereales'),
(19, 'Especias'),
(21, 'Fertilizantes'),
(9, 'Flores'),
(1, 'Frutas'),
(12, 'Frutos secos'),
(3, 'Hortalizas'),
(14, 'Huevos'),
(22, 'Insumos Agrícolas'),
(13, 'Lácteos'),
(5, 'Legumbres'),
(16, 'Miel'),
(23, 'Otros'),
(17, 'Pescados'),
(10, 'Plantas'),
(18, 'Semillas'),
(4, 'Tubérculos'),
(2, 'Verduras');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `citas`
--

CREATE TABLE `citas` (
  `id` int(11) NOT NULL,
  `solicitante_id` int(11) NOT NULL,
  `receptor_id` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `hora` time NOT NULL,
  `lugar` varchar(255) DEFAULT NULL,
  `motivo` varchar(255) NOT NULL,
  `mensaje` text DEFAULT NULL,
  `estado` enum('Pendiente','Aceptada','Rechazada','Cancelada','Completada') NOT NULL DEFAULT 'Pendiente',
  `creada_en` timestamp NOT NULL DEFAULT current_timestamp(),
  `actualizada_en` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `citas`
--

INSERT INTO `citas` (`id`, `solicitante_id`, `receptor_id`, `fecha`, `hora`, `lugar`, `motivo`, `mensaje`, `estado`, `creada_en`, `actualizada_en`) VALUES
(1, 4, 2, '2026-09-19', '10:00:00', 'Finca El Triunfo, Neiva', 'Visita para conocer el cultivo de manzana', 'Quisiera ver el proceso de cosecha antes de cerrar el pedido recurrente.', 'Pendiente', '2026-09-14 14:16:39', '2026-09-14 14:16:39'),
(2, 3, 2, '2026-09-24', '15:00:00', 'Oficina AgroExport, Bogotá', 'Negociación de contrato de suministro mensual', NULL, 'Aceptada', '2026-09-14 14:16:39', '2026-09-14 14:16:39'),
(3, 6, 5, '2026-09-04', '09:00:00', 'Vereda La Esperanza, Marinilla', 'Recogida de pedido de quesos y lácteos', NULL, 'Completada', '2026-09-14 14:16:39', '2026-09-14 14:16:39'),
(4, 7, 5, '2026-09-17', '11:00:00', 'Planta de procesamiento, Cali', 'Visita para certificación de calidad', NULL, 'Rechazada', '2026-09-14 14:16:39', '2026-09-14 14:16:39'),
(5, 8, 2, '2027-05-10', '10:00:00', 'Mi casa BB', 'sexo', 'LLeva condon', 'Completada', '2026-09-21 14:27:54', '2026-09-21 14:28:09'),
(6, 10, 8, '2026-09-25', '15:20:00', 'En la plaza', 'Cerrar contrato', NULL, 'Aceptada', '2026-09-21 15:19:45', '2026-09-21 15:19:59'),
(7, 8, 2, '2026-10-02', '17:50:00', 'a', 'a', 'a', 'Pendiente', '2026-09-21 15:47:52', '2026-09-21 15:47:52'),
(8, 8, 2, '2026-09-24', '00:50:00', 'Mi casa BB', 'Cerrar contrato', 'a', 'Pendiente', '2026-09-21 15:48:11', '2026-09-21 15:48:11'),
(9, 2, 8, '2026-09-24', '15:55:00', 'A', 'A', NULL, 'Pendiente', '2026-09-21 15:49:26', '2026-09-21 15:49:26'),
(10, 8, 2, '2026-10-09', '04:55:00', 'En la plaza', 'A', NULL, 'Pendiente', '2026-09-21 15:50:29', '2026-09-21 15:50:29');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `comentarios`
--

CREATE TABLE `comentarios` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `texto` varchar(300) NOT NULL,
  `estado` enum('Publicado','Oculto') NOT NULL DEFAULT 'Publicado',
  `creado_en` timestamp NOT NULL DEFAULT current_timestamp(),
  `actualizado_en` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `comentarios`
--

INSERT INTO `comentarios` (`id`, `usuario_id`, `texto`, `estado`, `creado_en`, `actualizado_en`) VALUES
(2, 3, 'La transparencia en el inventario y la comunicación directa con los productores nos ha ahorrado mucho tiempo de logística en cada compra.', 'Publicado', '2026-09-16 15:03:29', '2026-09-16 15:03:29'),
(3, 4, 'Comparar precios entre vendedores me ayuda a comprar mejor. El historial de precios es muy útil para saber cuándo conviene negociar.', 'Publicado', '2026-09-17 15:03:29', '2026-09-17 15:03:29'),
(4, 5, 'Me gusta ver los pedidos que llegan y aceptarlos desde el celular. La plataforma es fácil de usar incluso para quienes no somos expertos en tecnología.', 'Publicado', '2026-09-18 15:03:29', '2026-09-18 15:03:29'),
(5, 6, 'Encontré productores de mi zona con muy buen producto y a buen precio. El chat directo hace que todo sea más rápido.', 'Publicado', '2026-09-19 15:03:29', '2026-09-19 15:03:29'),
(6, 7, 'Pedimos a varios productores en un mismo carrito y cada uno atiende su parte del pedido. Nos organiza mucho el abastecimiento.', 'Publicado', '2026-09-20 15:03:29', '2026-09-20 15:03:29');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `comerciantes`
--

CREATE TABLE `comerciantes` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `ubicacion_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `comerciantes`
--

INSERT INTO `comerciantes` (`id`, `usuario_id`, `telefono`, `ubicacion_id`) VALUES
(1, 4, '3155554433', 3),
(2, 6, '3201234567', 3),
(3, 8, '3213260180', 6),
(4, 9, '310 5881813', 7);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `departamentos`
--

CREATE TABLE `departamentos` (
  `id` int(11) NOT NULL COMMENT 'Código DANE del departamento',
  `nombre` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `departamentos`
--

INSERT INTO `departamentos` (`id`, `nombre`) VALUES
(91, 'Amazonas'),
(5, 'Antioquia'),
(81, 'Arauca'),
(88, 'Archipiélago de San Andrés, Providencia y Santa Catalina'),
(8, 'Atlántico'),
(11, 'Bogotá D.C.'),
(13, 'Bolívar'),
(15, 'Boyacá'),
(17, 'Caldas'),
(18, 'Caquetá'),
(85, 'Casanare'),
(19, 'Cauca'),
(20, 'Cesar'),
(27, 'Chocó'),
(23, 'Córdoba'),
(25, 'Cundinamarca'),
(94, 'Guainía'),
(95, 'Guaviare'),
(41, 'Huila'),
(44, 'La Guajira'),
(47, 'Magdalena'),
(50, 'Meta'),
(52, 'Nariño'),
(54, 'Norte de Santander'),
(86, 'Putumayo'),
(63, 'Quindío'),
(66, 'Risaralda'),
(68, 'Santander'),
(70, 'Sucre'),
(73, 'Tolima'),
(76, 'Valle del Cauca'),
(97, 'Vaupés'),
(99, 'Vichada');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_pedidos`
--

CREATE TABLE `detalle_pedidos` (
  `id` int(11) NOT NULL,
  `pedido_id` int(11) NOT NULL,
  `publicacion_id` int(11) NOT NULL,
  `cantidad` float NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `detalle_pedidos`
--

INSERT INTO `detalle_pedidos` (`id`, `pedido_id`, `publicacion_id`, `cantidad`, `precio_unitario`) VALUES
(1, 1, 2, 20, 5000.00),
(2, 1, 3, 15, 3200.00),
(3, 2, 15, 10, 22000.00),
(4, 3, 10, 8, 6800.00),
(5, 4, 24, 12, 14500.00),
(6, 4, 29, 6, 16500.00),
(7, 5, 3, 25, 3200.00),
(8, 6, 2, 10, 5000.00),
(9, 7, 14, 5, 800000.00),
(10, 8, 15, 50, 22000.00),
(11, 9, 63, 25, 260000.00),
(12, 10, 63, 50, 260000.00),
(13, 11, 63, 50, 320000.00),
(14, 12, 63, 85, 320000.00),
(15, 13, 63, 25, 320000.00),
(16, 14, 64, 80, 70000.00),
(17, 15, 63, 15, 320000.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `empresas`
--

CREATE TABLE `empresas` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `nit` varchar(20) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `ubicacion_id` int(11) DEFAULT NULL,
  `sector` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `empresas`
--

INSERT INTO `empresas` (`id`, `usuario_id`, `nit`, `telefono`, `ubicacion_id`, `sector`) VALUES
(1, 3, '900123456-7', '3209876543', 2, 'Exportación'),
(2, 7, '900123456-7', '3109876543', 5, 'Distribución de alimentos');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `favoritos`
--

CREATE TABLE `favoritos` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `publicacion_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `favoritos`
--

INSERT INTO `favoritos` (`id`, `usuario_id`, `publicacion_id`) VALUES
(1, 4, 15),
(2, 4, 10),
(3, 3, 16),
(4, 6, 3),
(5, 7, 24),
(6, 7, 29);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historial`
--

CREATE TABLE `historial` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `accion` varchar(255) NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historial_precios`
--

CREATE TABLE `historial_precios` (
  `id` int(11) NOT NULL,
  `publicacion_id` int(11) NOT NULL,
  `tipo_precio` enum('empresa','comerciante') NOT NULL DEFAULT 'comerciante',
  `precio_anterior` decimal(10,2) NOT NULL,
  `precio_nuevo` decimal(10,2) NOT NULL,
  `fecha_cambio` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `historial_precios`
--

INSERT INTO `historial_precios` (`id`, `publicacion_id`, `tipo_precio`, `precio_anterior`, `precio_nuevo`, `fecha_cambio`) VALUES
(2, 2, 'comerciante', 5000.00, 5000.00, '2026-09-08 12:52:53'),
(4, 3, 'comerciante', 3200.00, 3200.00, '2026-09-08 12:53:29'),
(5, 4, 'comerciante', 1800.00, 1800.00, '2026-09-08 12:53:30'),
(6, 5, 'comerciante', 2500.00, 2500.00, '2026-09-08 12:53:32'),
(7, 6, 'comerciante', 1600.00, 1600.00, '2026-09-08 12:53:34'),
(8, 7, 'comerciante', 2200.00, 2200.00, '2026-09-08 12:53:35'),
(9, 8, 'comerciante', 1900.00, 1900.00, '2026-09-08 12:53:36'),
(10, 9, 'comerciante', 1500.00, 1500.00, '2026-09-08 12:53:36'),
(11, 10, 'comerciante', 6800.00, 6800.00, '2026-09-08 12:53:36'),
(12, 11, 'comerciante', 7200.00, 7200.00, '2026-09-08 12:53:37'),
(13, 12, 'comerciante', 1700.00, 1700.00, '2026-09-08 12:53:37'),
(14, 13, 'comerciante', 3200.00, 3200.00, '2026-09-08 12:53:37'),
(15, 14, 'comerciante', 15500.00, 15500.00, '2026-09-08 12:53:38'),
(16, 15, 'comerciante', 22000.00, 22000.00, '2026-09-08 12:53:38'),
(17, 16, 'comerciante', 13500.00, 13500.00, '2026-09-08 12:53:38'),
(18, 17, 'comerciante', 900.00, 900.00, '2026-09-08 12:53:39'),
(19, 18, 'comerciante', 700.00, 700.00, '2026-09-08 12:53:39'),
(20, 19, 'comerciante', 4500.00, 4500.00, '2026-09-08 12:53:39'),
(21, 20, 'comerciante', 2000.00, 2000.00, '2026-09-08 12:53:40'),
(22, 21, 'comerciante', 1200.00, 1200.00, '2026-09-08 12:53:40'),
(23, 22, 'comerciante', 28000.00, 28000.00, '2026-09-08 12:53:40'),
(24, 23, 'comerciante', 32000.00, 32000.00, '2026-09-08 12:53:41'),
(25, 24, 'comerciante', 14500.00, 14500.00, '2026-09-08 12:53:41'),
(26, 25, 'comerciante', 2600.00, 2600.00, '2026-09-08 12:53:41'),
(27, 26, 'comerciante', 13000.00, 13000.00, '2026-09-08 12:53:42'),
(28, 27, 'comerciante', 11500.00, 11500.00, '2026-09-08 12:53:42'),
(29, 28, 'comerciante', 24000.00, 24000.00, '2026-09-08 12:53:42'),
(30, 29, 'comerciante', 16500.00, 16500.00, '2026-09-08 12:53:43'),
(31, 30, 'comerciante', 9500.00, 9500.00, '2026-09-08 12:53:43'),
(32, 31, 'comerciante', 26000.00, 26000.00, '2026-09-08 12:53:43'),
(33, 32, 'comerciante', 8500.00, 8500.00, '2026-09-08 12:53:44'),
(34, 2, 'empresa', 5000.00, 5000.00, '2026-09-08 12:52:53'),
(35, 3, 'empresa', 3200.00, 3200.00, '2026-09-08 12:53:29'),
(36, 4, 'empresa', 1800.00, 1800.00, '2026-09-08 12:53:30'),
(37, 5, 'empresa', 2500.00, 2500.00, '2026-09-08 12:53:32'),
(38, 6, 'empresa', 1600.00, 1600.00, '2026-09-08 12:53:34'),
(39, 7, 'empresa', 2200.00, 2200.00, '2026-09-08 12:53:35'),
(40, 8, 'empresa', 1900.00, 1900.00, '2026-09-08 12:53:36'),
(41, 9, 'empresa', 1500.00, 1500.00, '2026-09-08 12:53:36'),
(42, 10, 'empresa', 6800.00, 6800.00, '2026-09-08 12:53:36'),
(43, 11, 'empresa', 7200.00, 7200.00, '2026-09-08 12:53:37'),
(44, 12, 'empresa', 1700.00, 1700.00, '2026-09-08 12:53:37'),
(45, 13, 'empresa', 3200.00, 3200.00, '2026-09-08 12:53:37'),
(46, 14, 'empresa', 15500.00, 15500.00, '2026-09-08 12:53:38'),
(47, 15, 'empresa', 22000.00, 22000.00, '2026-09-08 12:53:38'),
(48, 16, 'empresa', 13500.00, 13500.00, '2026-09-08 12:53:38'),
(49, 17, 'empresa', 900.00, 900.00, '2026-09-08 12:53:39'),
(50, 18, 'empresa', 700.00, 700.00, '2026-09-08 12:53:39'),
(51, 19, 'empresa', 4500.00, 4500.00, '2026-09-08 12:53:39'),
(52, 20, 'empresa', 2000.00, 2000.00, '2026-09-08 12:53:40'),
(53, 21, 'empresa', 1200.00, 1200.00, '2026-09-08 12:53:40'),
(54, 22, 'empresa', 28000.00, 28000.00, '2026-09-08 12:53:40'),
(55, 23, 'empresa', 32000.00, 32000.00, '2026-09-08 12:53:41'),
(56, 24, 'empresa', 14500.00, 14500.00, '2026-09-08 12:53:41'),
(57, 25, 'empresa', 2600.00, 2600.00, '2026-09-08 12:53:41'),
(58, 26, 'empresa', 13000.00, 13000.00, '2026-09-08 12:53:42'),
(59, 27, 'empresa', 11500.00, 11500.00, '2026-09-08 12:53:42'),
(60, 28, 'empresa', 24000.00, 24000.00, '2026-09-08 12:53:42'),
(61, 29, 'empresa', 16500.00, 16500.00, '2026-09-08 12:53:43'),
(62, 30, 'empresa', 9500.00, 9500.00, '2026-09-08 12:53:43'),
(63, 31, 'empresa', 26000.00, 26000.00, '2026-09-08 12:53:43'),
(64, 32, 'empresa', 8500.00, 8500.00, '2026-09-08 12:53:44'),
(65, 14, 'empresa', 15500.00, 800000.00, '2026-09-14 13:41:52'),
(66, 2, 'empresa', 4000.00, 4000.00, '2026-06-16 14:16:39'),
(67, 2, 'comerciante', 4000.00, 4000.00, '2026-06-16 14:16:39'),
(68, 2, 'empresa', 4000.00, 4500.00, '2026-07-16 14:16:39'),
(69, 2, 'comerciante', 4000.00, 4500.00, '2026-07-16 14:16:39'),
(70, 2, 'empresa', 4500.00, 5000.00, '2026-08-15 14:16:39'),
(71, 2, 'comerciante', 4500.00, 5000.00, '2026-08-15 14:16:39'),
(72, 3, 'empresa', 3850.00, 3850.00, '2026-06-16 14:16:39'),
(73, 3, 'comerciante', 3850.00, 3850.00, '2026-06-16 14:16:39'),
(74, 3, 'empresa', 3850.00, 3500.00, '2026-07-16 14:16:39'),
(75, 3, 'comerciante', 3850.00, 3500.00, '2026-07-16 14:16:39'),
(76, 3, 'empresa', 3500.00, 3200.00, '2026-08-15 14:16:39'),
(77, 3, 'comerciante', 3500.00, 3200.00, '2026-08-15 14:16:39'),
(78, 15, 'empresa', 17600.00, 17600.00, '2026-06-16 14:16:39'),
(79, 15, 'comerciante', 17600.00, 17600.00, '2026-06-16 14:16:39'),
(80, 15, 'empresa', 17600.00, 19800.00, '2026-07-16 14:16:39'),
(81, 15, 'comerciante', 17600.00, 19800.00, '2026-07-16 14:16:39'),
(82, 15, 'empresa', 19800.00, 22000.00, '2026-08-15 14:16:39'),
(83, 15, 'comerciante', 19800.00, 22000.00, '2026-08-15 14:16:39'),
(84, 24, 'empresa', 17400.00, 17400.00, '2026-06-16 14:16:39'),
(85, 24, 'comerciante', 17400.00, 17400.00, '2026-06-16 14:16:39'),
(86, 24, 'empresa', 17400.00, 15950.00, '2026-07-16 14:16:39'),
(87, 24, 'comerciante', 17400.00, 15950.00, '2026-07-16 14:16:39'),
(88, 24, 'empresa', 15950.00, 14500.00, '2026-08-15 14:16:39'),
(89, 24, 'comerciante', 15950.00, 14500.00, '2026-08-15 14:16:39'),
(150, 63, 'empresa', 250000.00, 250000.00, '2026-09-21 15:14:19'),
(151, 63, 'comerciante', 260000.00, 260000.00, '2026-09-21 15:14:19'),
(152, 63, 'empresa', 250000.00, 300000.00, '2026-09-21 15:20:56'),
(153, 63, 'comerciante', 260000.00, 320000.00, '2026-09-21 15:20:56'),
(154, 64, 'empresa', 80000.00, 80000.00, '2026-09-21 15:58:53'),
(155, 64, 'comerciante', 70000.00, 70000.00, '2026-09-21 15:58:53');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `mensajes`
--

CREATE TABLE `mensajes` (
  `id` int(11) NOT NULL,
  `remitente_id` int(11) NOT NULL,
  `destinatario_id` int(11) NOT NULL,
  `contenido` text NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `leido` tinyint(1) DEFAULT 0,
  `editado_en` timestamp NULL DEFAULT NULL,
  `eliminado_para_todos` tinyint(1) NOT NULL DEFAULT 0,
  `oculto_remitente` tinyint(1) NOT NULL DEFAULT 0,
  `oculto_destinatario` tinyint(1) NOT NULL DEFAULT 0,
  `respuesta_a_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `mensajes`
--

INSERT INTO `mensajes` (`id`, `remitente_id`, `destinatario_id`, `contenido`, `fecha`, `leido`, `editado_en`, `eliminado_para_todos`, `oculto_remitente`, `oculto_destinatario`, `respuesta_a_id`) VALUES
(2, 4, 2, 'Hola Juan, vi tu publicación de Manzana Roja, ¿tienes disponibilidad para 20 libras semanales?', '2026-09-11 14:16:39', 1, NULL, 0, 0, 0, NULL),
(3, 2, 4, '¡Hola Pedro! Sí, con gusto. Puedo dejarte reservado ese volumen cada semana.', '2026-09-11 15:16:39', 1, NULL, 0, 0, 0, NULL),
(4, 4, 2, 'Perfecto, ¿manejas algún descuento por volumen?', '2026-09-12 16:16:39', 1, NULL, 0, 0, 0, NULL),
(5, 2, 4, 'Claro, para pedidos recurrentes puedo mejorar un poco el precio. Te escribo la propuesta.', '2026-09-12 17:16:39', 1, NULL, 0, 0, 0, NULL),
(6, 4, 2, '¡Excelente, quedo atento!', '2026-09-13 18:16:39', 1, NULL, 0, 0, 0, NULL),
(7, 6, 5, 'Hola María, ¿tienes Queso Campesino disponible esta semana?', '2026-09-11 14:16:39', 1, NULL, 0, 0, 0, NULL),
(8, 5, 6, 'Hola Laura, sí tengo disponible. ¿Cuánto necesitas?', '2026-09-11 15:16:39', 1, NULL, 0, 0, 0, NULL),
(9, 6, 5, 'Unos 12 kg, para el próximo miércoles si es posible.', '2026-09-12 16:16:39', 1, NULL, 0, 0, 0, NULL),
(10, 5, 6, 'Perfecto, te lo puedo tener listo para esa fecha.', '2026-09-12 17:16:39', 1, NULL, 0, 0, 0, NULL),
(11, 6, 5, '¡Genial, muchas gracias!', '2026-09-13 18:16:39', 0, NULL, 0, 0, 0, NULL),
(12, 7, 5, 'Buen día, queremos cotizar Trucha Arcoíris para nuestro punto de distribución.', '2026-09-11 14:16:39', 1, NULL, 0, 0, 0, NULL),
(13, 5, 7, 'Hola, con gusto te comparto precios. ¿Qué volumen manejan normalmente?', '2026-09-11 15:16:39', 1, NULL, 0, 0, 0, NULL),
(14, 7, 5, 'Entre 30 y 50 kg por pedido, dependiendo de la temporada.', '2026-09-12 16:16:39', 1, NULL, 0, 0, 0, NULL),
(15, 8, 2, '', '2026-09-21 14:26:52', 1, NULL, 1, 0, 0, NULL),
(16, 8, 2, '', '2026-09-21 14:26:56', 1, NULL, 1, 0, 0, NULL),
(17, 8, 10, 'puedo tener mas sacos con usted', '2026-09-21 15:16:25', 1, NULL, 0, 0, 0, NULL),
(18, 10, 8, 'En 20 dias otros 50', '2026-09-21 15:16:49', 1, NULL, 0, 0, 0, NULL),
(19, 8, 2, 'hl', '2026-09-21 16:13:02', 1, NULL, 0, 0, 0, NULL);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `municipios`
--

CREATE TABLE `municipios` (
  `id` int(11) NOT NULL COMMENT 'Código DANE del municipio',
  `departamento_id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `municipios`
--

INSERT INTO `municipios` (`id`, `departamento_id`, `nombre`) VALUES
(5002, 5, 'Abejorral'),
(5004, 5, 'Abriaquí'),
(5021, 5, 'Alejandría'),
(5030, 5, 'Amagá'),
(5031, 5, 'Amalfi'),
(5034, 5, 'Andes'),
(5036, 5, 'Angelópolis'),
(5038, 5, 'Angostura'),
(5040, 5, 'Anorí'),
(5044, 5, 'Anzá'),
(5045, 5, 'Apartadó'),
(5051, 5, 'Arboletes'),
(5055, 5, 'Argelia'),
(5059, 5, 'Armenia'),
(5079, 5, 'Barbosa'),
(5088, 5, 'Bello'),
(5086, 5, 'Belmira'),
(5091, 5, 'Betania'),
(5093, 5, 'Betulia'),
(5107, 5, 'Briceño'),
(5113, 5, 'Buriticá'),
(5120, 5, 'Cáceres'),
(5125, 5, 'Caicedo'),
(5129, 5, 'Caldas'),
(5134, 5, 'Campamento'),
(5138, 5, 'Cañasgordas'),
(5142, 5, 'Caracolí'),
(5145, 5, 'Caramanta'),
(5147, 5, 'Carepa'),
(5150, 5, 'Carolina'),
(5154, 5, 'Caucasia'),
(5172, 5, 'Chigorodó'),
(5190, 5, 'Cisneros'),
(5101, 5, 'Ciudad Bolívar'),
(5197, 5, 'Cocorná'),
(5206, 5, 'Concepción'),
(5209, 5, 'Concordia'),
(5212, 5, 'Copacabana'),
(5234, 5, 'Dabeiba'),
(5237, 5, 'Donmatías'),
(5240, 5, 'Ebéjico'),
(5250, 5, 'El Bagre'),
(5148, 5, 'El Carmen de Viboral'),
(5697, 5, 'El Santuario'),
(5264, 5, 'Entrerríos'),
(5266, 5, 'Envigado'),
(5282, 5, 'Fredonia'),
(5284, 5, 'Frontino'),
(5306, 5, 'Giraldo'),
(5308, 5, 'Girardota'),
(5310, 5, 'Gómez Plata'),
(5313, 5, 'Granada'),
(5315, 5, 'Guadalupe'),
(5318, 5, 'Guarne'),
(5321, 5, 'Guatapé'),
(5347, 5, 'Heliconia'),
(5353, 5, 'Hispania'),
(5360, 5, 'Itagüí'),
(5361, 5, 'Ituango'),
(5364, 5, 'Jardín'),
(5368, 5, 'Jericó'),
(5376, 5, 'La Ceja'),
(5380, 5, 'La Estrella'),
(5390, 5, 'La Pintada'),
(5400, 5, 'La Unión'),
(5411, 5, 'Liborina'),
(5425, 5, 'Maceo'),
(5440, 5, 'Marinilla'),
(5001, 5, 'Medellín'),
(5467, 5, 'Montebello'),
(5475, 5, 'Murindó'),
(5480, 5, 'Mutatá'),
(5483, 5, 'Nariño'),
(5495, 5, 'Nechí'),
(5490, 5, 'Necoclí'),
(5501, 5, 'Olaya'),
(5541, 5, 'Peñol'),
(5543, 5, 'Peque'),
(5576, 5, 'Pueblorrico'),
(5579, 5, 'Puerto Berrío'),
(5585, 5, 'Puerto Nare'),
(5591, 5, 'Puerto Triunfo'),
(5604, 5, 'Remedios'),
(5607, 5, 'Retiro'),
(5615, 5, 'Rionegro'),
(5628, 5, 'Sabanalarga'),
(5631, 5, 'Sabaneta'),
(5642, 5, 'Salgar'),
(5647, 5, 'San Andrés de Cuerquía'),
(5649, 5, 'San Carlos'),
(5652, 5, 'San Francisco'),
(5656, 5, 'San Jerónimo'),
(5658, 5, 'San José de la Montaña'),
(5659, 5, 'San Juan de Urabá'),
(5660, 5, 'San Luis'),
(5664, 5, 'San Pedro de los Milagros'),
(5665, 5, 'San Pedro de Urabá'),
(5667, 5, 'San Rafael'),
(5670, 5, 'San Roque'),
(5674, 5, 'San Vicente Ferrer'),
(5679, 5, 'Santa Bárbara'),
(5042, 5, 'Santa Fé de Antioquia'),
(5686, 5, 'Santa Rosa de Osos'),
(5690, 5, 'Santo Domingo'),
(5736, 5, 'Segovia'),
(5756, 5, 'Sonsón'),
(5761, 5, 'Sopetrán'),
(5789, 5, 'Támesis'),
(5790, 5, 'Tarazá'),
(5792, 5, 'Tarso'),
(5809, 5, 'Titiribí'),
(5819, 5, 'Toledo'),
(5837, 5, 'Turbo'),
(5842, 5, 'Uramita'),
(5847, 5, 'Urrao'),
(5854, 5, 'Valdivia'),
(5856, 5, 'Valparaíso'),
(5858, 5, 'Vegachí'),
(5861, 5, 'Venecia'),
(5873, 5, 'Vigía del Fuerte'),
(5885, 5, 'Yalí'),
(5887, 5, 'Yarumal'),
(5890, 5, 'Yolombó'),
(5893, 5, 'Yondó'),
(5895, 5, 'Zaragoza'),
(8078, 8, 'Baranoa'),
(8001, 8, 'Barranquilla'),
(8137, 8, 'Campo de la Cruz'),
(8141, 8, 'Candelaria'),
(8296, 8, 'Galapa'),
(8372, 8, 'Juan de Acosta'),
(8421, 8, 'Luruaco'),
(8433, 8, 'Malambo'),
(8436, 8, 'Manatí'),
(8520, 8, 'Palmar de Varela'),
(8549, 8, 'Piojó'),
(8558, 8, 'Polonuevo'),
(8560, 8, 'Ponedera'),
(8573, 8, 'Puerto Colombia'),
(8606, 8, 'Repelón'),
(8634, 8, 'Sabanagrande'),
(8638, 8, 'Sabanalarga'),
(8675, 8, 'Santa Lucía'),
(8685, 8, 'Santo Tomás'),
(8758, 8, 'Soledad'),
(8770, 8, 'Suan'),
(8832, 8, 'Tubará'),
(8849, 8, 'Usiacurí'),
(11001, 11, 'Bogotá'),
(13006, 13, 'Achí'),
(13030, 13, 'Altos del Rosario'),
(13042, 13, 'Arenal'),
(13052, 13, 'Arjona'),
(13062, 13, 'Arroyohondo'),
(13074, 13, 'Barranco de Loba'),
(13140, 13, 'Calamar'),
(13160, 13, 'Cantagallo'),
(13001, 13, 'Cartagena de Indias'),
(13188, 13, 'Cicuco'),
(13222, 13, 'Clemencia'),
(13212, 13, 'Córdoba'),
(13244, 13, 'El Carmen de Bolívar'),
(13248, 13, 'El Guamo'),
(13268, 13, 'El Peñón'),
(13300, 13, 'Hatillo de Loba'),
(13430, 13, 'Magangué'),
(13433, 13, 'Mahates'),
(13440, 13, 'Margarita'),
(13442, 13, 'María la Baja'),
(13458, 13, 'Montecristo'),
(13473, 13, 'Morales'),
(13490, 13, 'Norosí'),
(13549, 13, 'Pinillos'),
(13580, 13, 'Regidor'),
(13600, 13, 'Río Viejo'),
(13620, 13, 'San Cristóbal'),
(13647, 13, 'San Estanislao'),
(13650, 13, 'San Fernando'),
(13654, 13, 'San Jacinto'),
(13655, 13, 'San Jacinto del Cauca'),
(13657, 13, 'San Juan Nepomuceno'),
(13667, 13, 'San Martín de Loba'),
(13670, 13, 'San Pablo'),
(13673, 13, 'Santa Catalina'),
(13468, 13, 'Santa Cruz de Mompox'),
(13683, 13, 'Santa Rosa'),
(13688, 13, 'Santa Rosa del Sur'),
(13744, 13, 'Simití'),
(13760, 13, 'Soplaviento'),
(13780, 13, 'Talaigua Nuevo'),
(13810, 13, 'Tiquisio'),
(13836, 13, 'Turbaco'),
(13838, 13, 'Turbaná'),
(13873, 13, 'Villanueva'),
(13894, 13, 'Zambrano'),
(15022, 15, 'Almeida'),
(15047, 15, 'Aquitania'),
(15051, 15, 'Arcabuco'),
(15087, 15, 'Belén'),
(15090, 15, 'Berbeo'),
(15092, 15, 'Betéitiva'),
(15097, 15, 'Boavita'),
(15104, 15, 'Boyacá'),
(15106, 15, 'Briceño'),
(15109, 15, 'Buenavista'),
(15114, 15, 'Busbanzá'),
(15131, 15, 'Caldas'),
(15135, 15, 'Campohermoso'),
(15162, 15, 'Cerinza'),
(15172, 15, 'Chinavita'),
(15176, 15, 'Chiquinquirá'),
(15232, 15, 'Chíquiza'),
(15180, 15, 'Chiscas'),
(15183, 15, 'Chita'),
(15185, 15, 'Chitaraque'),
(15187, 15, 'Chivatá'),
(15236, 15, 'Chivor'),
(15189, 15, 'Ciénega'),
(15204, 15, 'Cómbita'),
(15212, 15, 'Coper'),
(15215, 15, 'Corrales'),
(15218, 15, 'Covarachía'),
(15223, 15, 'Cubará'),
(15224, 15, 'Cucaita'),
(15226, 15, 'Cuítiva'),
(15238, 15, 'Duitama'),
(15244, 15, 'El Cocuy'),
(15248, 15, 'El Espino'),
(15272, 15, 'Firavitoba'),
(15276, 15, 'Floresta'),
(15293, 15, 'Gachantivá'),
(15296, 15, 'Gámeza'),
(15299, 15, 'Garagoa'),
(15317, 15, 'Guacamayas'),
(15322, 15, 'Guateque'),
(15325, 15, 'Guayatá'),
(15332, 15, 'Güicán de la Sierra'),
(15362, 15, 'Iza'),
(15367, 15, 'Jenesano'),
(15368, 15, 'Jericó'),
(15380, 15, 'La Capilla'),
(15403, 15, 'La Uvita'),
(15401, 15, 'La Victoria'),
(15377, 15, 'Labranzagrande'),
(15425, 15, 'Macanal'),
(15442, 15, 'Maripí'),
(15455, 15, 'Miraflores'),
(15464, 15, 'Mongua'),
(15466, 15, 'Monguí'),
(15469, 15, 'Moniquirá'),
(15476, 15, 'Motavita'),
(15480, 15, 'Muzo'),
(15491, 15, 'Nobsa'),
(15494, 15, 'Nuevo Colón'),
(15500, 15, 'Oicatá'),
(15507, 15, 'Otanche'),
(15511, 15, 'Pachavita'),
(15514, 15, 'Páez'),
(15516, 15, 'Paipa'),
(15518, 15, 'Pajarito'),
(15522, 15, 'Panqueba'),
(15531, 15, 'Pauna'),
(15533, 15, 'Paya'),
(15537, 15, 'Paz de Río'),
(15542, 15, 'Pesca'),
(15550, 15, 'Pisba'),
(15572, 15, 'Puerto Boyacá'),
(15580, 15, 'Quípama'),
(15599, 15, 'Ramiriquí'),
(15600, 15, 'Ráquira'),
(15621, 15, 'Rondón'),
(15632, 15, 'Saboyá'),
(15638, 15, 'Sáchica'),
(15646, 15, 'Samacá'),
(15660, 15, 'San Eduardo'),
(15664, 15, 'San José de Pare'),
(15667, 15, 'San Luis de Gaceno'),
(15673, 15, 'San Mateo'),
(15676, 15, 'San Miguel de Sema'),
(15681, 15, 'San Pablo de Borbur'),
(15690, 15, 'Santa María'),
(15693, 15, 'Santa Rosa de Viterbo'),
(15696, 15, 'Santa Sofía'),
(15686, 15, 'Santana'),
(15720, 15, 'Sativanorte'),
(15723, 15, 'Sativasur'),
(15740, 15, 'Siachoque'),
(15753, 15, 'Soatá'),
(15757, 15, 'Socha'),
(15755, 15, 'Socotá'),
(15759, 15, 'Sogamoso'),
(15761, 15, 'Somondoco'),
(15762, 15, 'Sora'),
(15764, 15, 'Soracá'),
(15763, 15, 'Sotaquirá'),
(15774, 15, 'Susacón'),
(15776, 15, 'Sutamarchán'),
(15778, 15, 'Sutatenza'),
(15790, 15, 'Tasco'),
(15798, 15, 'Tenza'),
(15804, 15, 'Tibaná'),
(15806, 15, 'Tibasosa'),
(15808, 15, 'Tinjacá'),
(15810, 15, 'Tipacoque'),
(15814, 15, 'Toca'),
(15816, 15, 'Togüí'),
(15820, 15, 'Tópaga'),
(15822, 15, 'Tota'),
(15001, 15, 'Tunja'),
(15832, 15, 'Tununguá'),
(15835, 15, 'Turmequé'),
(15837, 15, 'Tuta'),
(15839, 15, 'Tutazá'),
(15842, 15, 'Úmbita'),
(15861, 15, 'Ventaquemada'),
(15407, 15, 'Villa de Leyva'),
(15879, 15, 'Viracachá'),
(15897, 15, 'Zetaquira'),
(17013, 17, 'Aguadas'),
(17042, 17, 'Anserma'),
(17050, 17, 'Aranzazu'),
(17088, 17, 'Belalcázar'),
(17174, 17, 'Chinchiná'),
(17272, 17, 'Filadelfia'),
(17380, 17, 'La Dorada'),
(17388, 17, 'La Merced'),
(17001, 17, 'Manizales'),
(17433, 17, 'Manzanares'),
(17442, 17, 'Marmato'),
(17444, 17, 'Marquetalia'),
(17446, 17, 'Marulanda'),
(17486, 17, 'Neira'),
(17495, 17, 'Norcasia'),
(17513, 17, 'Pácora'),
(17524, 17, 'Palestina'),
(17541, 17, 'Pensilvania'),
(17614, 17, 'Riosucio'),
(17616, 17, 'Risaralda'),
(17653, 17, 'Salamina'),
(17662, 17, 'Samaná'),
(17665, 17, 'San José'),
(17777, 17, 'Supía'),
(17867, 17, 'Victoria'),
(17873, 17, 'Villamaría'),
(17877, 17, 'Viterbo'),
(18029, 18, 'Albania'),
(18094, 18, 'Belén de los Andaquíes'),
(18150, 18, 'Cartagena del Chairá'),
(18205, 18, 'Curillo'),
(18247, 18, 'El Doncello'),
(18256, 18, 'El Paujíl'),
(18001, 18, 'Florencia'),
(18410, 18, 'La Montañita'),
(18460, 18, 'Milán'),
(18479, 18, 'Morelia'),
(18592, 18, 'Puerto Rico'),
(18610, 18, 'San José del Fragua'),
(18753, 18, 'San Vicente del Caguán'),
(18756, 18, 'Solano'),
(18785, 18, 'Solita'),
(18860, 18, 'Valparaíso'),
(19022, 19, 'Almaguer'),
(19050, 19, 'Argelia'),
(19075, 19, 'Balboa'),
(19100, 19, 'Bolívar'),
(19110, 19, 'Buenos Aires'),
(19130, 19, 'Cajibío'),
(19137, 19, 'Caldono'),
(19142, 19, 'Caloto'),
(19212, 19, 'Corinto'),
(19256, 19, 'El Tambo'),
(19290, 19, 'Florencia'),
(19300, 19, 'Guachené'),
(19318, 19, 'Guapi'),
(19355, 19, 'Inzá'),
(19364, 19, 'Jambaló'),
(19392, 19, 'La Sierra'),
(19397, 19, 'La Vega'),
(19418, 19, 'López de Micay'),
(19450, 19, 'Mercaderes'),
(19455, 19, 'Miranda'),
(19473, 19, 'Morales'),
(19513, 19, 'Padilla'),
(19517, 19, 'Páez'),
(19532, 19, 'Patía'),
(19533, 19, 'Piamonte'),
(19548, 19, 'Piendamó - Tunía'),
(19001, 19, 'Popayán'),
(19573, 19, 'Puerto Tejada'),
(19585, 19, 'Puracé'),
(19622, 19, 'Rosas'),
(19693, 19, 'San Sebastián'),
(19701, 19, 'Santa Rosa'),
(19698, 19, 'Santander de Quilichao'),
(19743, 19, 'Silvia'),
(19760, 19, 'Sotará - Paispamba'),
(19780, 19, 'Suárez'),
(19785, 19, 'Sucre'),
(19807, 19, 'Timbío'),
(19809, 19, 'Timbiquí'),
(19821, 19, 'Toribío'),
(19824, 19, 'Totoró'),
(19845, 19, 'Villa Rica'),
(20011, 20, 'Aguachica'),
(20013, 20, 'Agustín Codazzi'),
(20032, 20, 'Astrea'),
(20045, 20, 'Becerril'),
(20060, 20, 'Bosconia'),
(20175, 20, 'Chimichagua'),
(20178, 20, 'Chiriguaná'),
(20228, 20, 'Curumaní'),
(20238, 20, 'El Copey'),
(20250, 20, 'El Paso'),
(20295, 20, 'Gamarra'),
(20310, 20, 'González'),
(20383, 20, 'La Gloria'),
(20400, 20, 'La Jagua de Ibirico'),
(20621, 20, 'La Paz'),
(20443, 20, 'Manaure Balcón del Cesar'),
(20517, 20, 'Pailitas'),
(20550, 20, 'Pelaya'),
(20570, 20, 'Pueblo Bello'),
(20614, 20, 'Río de Oro'),
(20710, 20, 'San Alberto'),
(20750, 20, 'San Diego'),
(20770, 20, 'San Martín'),
(20787, 20, 'Tamalameque'),
(20001, 20, 'Valledupar'),
(23068, 23, 'Ayapel'),
(23079, 23, 'Buenavista'),
(23090, 23, 'Canalete'),
(23162, 23, 'Cereté'),
(23168, 23, 'Chimá'),
(23182, 23, 'Chinú'),
(23189, 23, 'Ciénaga de Oro'),
(23300, 23, 'Cotorra'),
(23350, 23, 'La Apartada'),
(23417, 23, 'Lorica'),
(23419, 23, 'Los Córdobas'),
(23464, 23, 'Momil'),
(23500, 23, 'Moñitos'),
(23466, 23, 'Montelíbano'),
(23001, 23, 'Montería'),
(23555, 23, 'Planeta Rica'),
(23570, 23, 'Pueblo Nuevo'),
(23574, 23, 'Puerto Escondido'),
(23580, 23, 'Puerto Libertador'),
(23586, 23, 'Purísima de la Concepción'),
(23660, 23, 'Sahagún'),
(23670, 23, 'San Andrés de Sotavento'),
(23672, 23, 'San Antero'),
(23675, 23, 'San Bernardo del Viento'),
(23678, 23, 'San Carlos'),
(23682, 23, 'San José de Uré'),
(23686, 23, 'San Pelayo'),
(23807, 23, 'Tierralta'),
(23815, 23, 'Tuchín'),
(23855, 23, 'Valencia'),
(25001, 25, 'Agua de Dios'),
(25019, 25, 'Albán'),
(25035, 25, 'Anapoima'),
(25040, 25, 'Anolaima'),
(25599, 25, 'Apulo'),
(25053, 25, 'Arbeláez'),
(25086, 25, 'Beltrán'),
(25095, 25, 'Bituima'),
(25099, 25, 'Bojacá'),
(25120, 25, 'Cabrera'),
(25123, 25, 'Cachipay'),
(25126, 25, 'Cajicá'),
(25148, 25, 'Caparrapí'),
(25151, 25, 'Cáqueza'),
(25154, 25, 'Carmen de Carupa'),
(25168, 25, 'Chaguaní'),
(25175, 25, 'Chía'),
(25178, 25, 'Chipaque'),
(25181, 25, 'Choachí'),
(25183, 25, 'Chocontá'),
(25200, 25, 'Cogua'),
(25214, 25, 'Cota'),
(25224, 25, 'Cucunubá'),
(25245, 25, 'El Colegio'),
(25258, 25, 'El Peñón'),
(25260, 25, 'El Rosal'),
(25269, 25, 'Facatativá'),
(25279, 25, 'Fómeque'),
(25281, 25, 'Fosca'),
(25286, 25, 'Funza'),
(25288, 25, 'Fúquene'),
(25290, 25, 'Fusagasugá'),
(25293, 25, 'Gachalá'),
(25295, 25, 'Gachancipá'),
(25297, 25, 'Gachetá'),
(25299, 25, 'Gama'),
(25307, 25, 'Girardot'),
(25312, 25, 'Granada'),
(25317, 25, 'Guachetá'),
(25320, 25, 'Guaduas'),
(25322, 25, 'Guasca'),
(25324, 25, 'Guataquí'),
(25326, 25, 'Guatavita'),
(25328, 25, 'Guayabal de Síquima'),
(25335, 25, 'Guayabetal'),
(25339, 25, 'Gutiérrez'),
(25368, 25, 'Jerusalén'),
(25372, 25, 'Junín'),
(25377, 25, 'La Calera'),
(25386, 25, 'La Mesa'),
(25394, 25, 'La Palma'),
(25398, 25, 'La Peña'),
(25402, 25, 'La Vega'),
(25407, 25, 'Lenguazaque'),
(25426, 25, 'Machetá'),
(25430, 25, 'Madrid'),
(25436, 25, 'Manta'),
(25438, 25, 'Medina'),
(25473, 25, 'Mosquera'),
(25483, 25, 'Nariño'),
(25486, 25, 'Nemocón'),
(25488, 25, 'Nilo'),
(25489, 25, 'Nimaima'),
(25491, 25, 'Nocaima'),
(25513, 25, 'Pacho'),
(25518, 25, 'Paime'),
(25524, 25, 'Pandi'),
(25530, 25, 'Paratebueno'),
(25535, 25, 'Pasca'),
(25572, 25, 'Puerto Salgar'),
(25580, 25, 'Pulí'),
(25592, 25, 'Quebradanegra'),
(25594, 25, 'Quetame'),
(25596, 25, 'Quipile'),
(25612, 25, 'Ricaurte'),
(25645, 25, 'San Antonio del Tequendama'),
(25649, 25, 'San Bernardo'),
(25653, 25, 'San Cayetano'),
(25658, 25, 'San Francisco'),
(25662, 25, 'San Juan de Rioseco'),
(25718, 25, 'Sasaima'),
(25736, 25, 'Sesquilé'),
(25740, 25, 'Sibaté'),
(25743, 25, 'Silvania'),
(25745, 25, 'Simijaca'),
(25754, 25, 'Soacha'),
(25758, 25, 'Sopó'),
(25769, 25, 'Subachoque'),
(25772, 25, 'Suesca'),
(25777, 25, 'Supatá'),
(25779, 25, 'Susa'),
(25781, 25, 'Sutatausa'),
(25785, 25, 'Tabio'),
(25793, 25, 'Tausa'),
(25797, 25, 'Tena'),
(25799, 25, 'Tenjo'),
(25805, 25, 'Tibacuy'),
(25807, 25, 'Tibirita'),
(25815, 25, 'Tocaima'),
(25817, 25, 'Tocancipá'),
(25823, 25, 'Topaipí'),
(25839, 25, 'Ubalá'),
(25841, 25, 'Ubaque'),
(25845, 25, 'Une'),
(25851, 25, 'Útica'),
(25506, 25, 'Venecia'),
(25862, 25, 'Vergara'),
(25867, 25, 'Vianí'),
(25843, 25, 'Villa de San Diego de Ubaté'),
(25871, 25, 'Villagómez'),
(25873, 25, 'Villapinzón'),
(25875, 25, 'Villeta'),
(25878, 25, 'Viotá'),
(25885, 25, 'Yacopí'),
(25898, 25, 'Zipacón'),
(25899, 25, 'Zipaquirá'),
(27006, 27, 'Acandí'),
(27025, 27, 'Alto Baudó'),
(27050, 27, 'Atrato'),
(27073, 27, 'Bagadó'),
(27075, 27, 'Bahía Solano'),
(27077, 27, 'Bajo Baudó'),
(27099, 27, 'Bojayá'),
(27150, 27, 'Carmen del Darién'),
(27160, 27, 'Cértegui'),
(27205, 27, 'Condoto'),
(27135, 27, 'El Cantón del San Pablo'),
(27245, 27, 'El Carmen de Atrato'),
(27250, 27, 'El Litoral del San Juan'),
(27361, 27, 'Istmina'),
(27372, 27, 'Juradó'),
(27413, 27, 'Lloró'),
(27425, 27, 'Medio Atrato'),
(27430, 27, 'Medio Baudó'),
(27450, 27, 'Medio San Juan'),
(27491, 27, 'Nóvita'),
(27493, 27, 'Nuevo Belén de Bajirá'),
(27495, 27, 'Nuquí'),
(27001, 27, 'Quibdó'),
(27580, 27, 'Río Iró'),
(27600, 27, 'Río Quito'),
(27615, 27, 'Riosucio'),
(27660, 27, 'San José del Palmar'),
(27745, 27, 'Sipí'),
(27787, 27, 'Tadó'),
(27800, 27, 'Unguía'),
(27810, 27, 'Unión Panamericana'),
(41006, 41, 'Acevedo'),
(41013, 41, 'Agrado'),
(41016, 41, 'Aipe'),
(41020, 41, 'Algeciras'),
(41026, 41, 'Altamira'),
(41078, 41, 'Baraya'),
(41132, 41, 'Campoalegre'),
(41206, 41, 'Colombia'),
(41244, 41, 'Elías'),
(41298, 41, 'Garzón'),
(41306, 41, 'Gigante'),
(41319, 41, 'Guadalupe'),
(41349, 41, 'Hobo'),
(41357, 41, 'Íquira'),
(41359, 41, 'Isnos'),
(41378, 41, 'La Argentina'),
(41396, 41, 'La Plata'),
(41483, 41, 'Nátaga'),
(41001, 41, 'Neiva'),
(41503, 41, 'Oporapa'),
(41518, 41, 'Paicol'),
(41524, 41, 'Palermo'),
(41530, 41, 'Palestina'),
(41548, 41, 'Pital'),
(41551, 41, 'Pitalito'),
(41615, 41, 'Rivera'),
(41660, 41, 'Saladoblanco'),
(41668, 41, 'San Agustín'),
(41676, 41, 'Santa María'),
(41770, 41, 'Suaza'),
(41791, 41, 'Tarqui'),
(41799, 41, 'Tello'),
(41801, 41, 'Teruel'),
(41797, 41, 'Tesalia'),
(41807, 41, 'Timaná'),
(41872, 41, 'Villavieja'),
(41885, 41, 'Yaguará'),
(44035, 44, 'Albania'),
(44078, 44, 'Barrancas'),
(44090, 44, 'Dibulla'),
(44098, 44, 'Distracción'),
(44110, 44, 'El Molino'),
(44279, 44, 'Fonseca'),
(44378, 44, 'Hatonuevo'),
(44420, 44, 'La Jagua del Pilar'),
(44430, 44, 'Maicao'),
(44560, 44, 'Manaure'),
(44001, 44, 'Riohacha'),
(44650, 44, 'San Juan del Cesar'),
(44847, 44, 'Uribia'),
(44855, 44, 'Urumita'),
(44874, 44, 'Villanueva'),
(47030, 47, 'Algarrobo'),
(47053, 47, 'Aracataca'),
(47058, 47, 'Ariguaní'),
(47161, 47, 'Cerro de San Antonio'),
(47170, 47, 'Chivolo'),
(47189, 47, 'Ciénaga'),
(47205, 47, 'Concordia'),
(47245, 47, 'El Banco'),
(47258, 47, 'El Piñón'),
(47268, 47, 'El Retén'),
(47288, 47, 'Fundación'),
(47318, 47, 'Guamal'),
(47460, 47, 'Nueva Granada'),
(47541, 47, 'Pedraza'),
(47545, 47, 'Pijiño del Carmen'),
(47551, 47, 'Pivijay'),
(47555, 47, 'Plato'),
(47570, 47, 'Puebloviejo'),
(47605, 47, 'Remolino'),
(47660, 47, 'Sabanas de San Ángel'),
(47675, 47, 'Salamina'),
(47692, 47, 'San Sebastián de Buenavista'),
(47703, 47, 'San Zenón'),
(47707, 47, 'Santa Ana'),
(47720, 47, 'Santa Bárbara de Pinto'),
(47001, 47, 'Santa Marta'),
(47745, 47, 'Sitionuevo'),
(47798, 47, 'Tenerife'),
(47960, 47, 'Zapayán'),
(47980, 47, 'Zona Bananera'),
(50006, 50, 'Acacías'),
(50110, 50, 'Barranca de Upía'),
(50124, 50, 'Cabuyaro'),
(50150, 50, 'Castilla la Nueva'),
(50223, 50, 'Cubarral'),
(50226, 50, 'Cumaral'),
(50245, 50, 'El Calvario'),
(50251, 50, 'El Castillo'),
(50270, 50, 'El Dorado'),
(50287, 50, 'Fuente de Oro'),
(50313, 50, 'Granada'),
(50318, 50, 'Guamal'),
(50350, 50, 'La Macarena'),
(50400, 50, 'Lejanías'),
(50325, 50, 'Mapiripán'),
(50330, 50, 'Mesetas'),
(50450, 50, 'Puerto Concordia'),
(50568, 50, 'Puerto Gaitán'),
(50577, 50, 'Puerto Lleras'),
(50573, 50, 'Puerto López'),
(50590, 50, 'Puerto Rico'),
(50606, 50, 'Restrepo'),
(50680, 50, 'San Carlos de Guaroa'),
(50683, 50, 'San Juan de Arama'),
(50686, 50, 'San Juanito'),
(50689, 50, 'San Martín'),
(50370, 50, 'Uribe'),
(50001, 50, 'Villavicencio'),
(50711, 50, 'Vistahermosa'),
(52019, 52, 'Albán'),
(52022, 52, 'Aldana'),
(52036, 52, 'Ancuya'),
(52051, 52, 'Arboleda'),
(52079, 52, 'Barbacoas'),
(52083, 52, 'Belén'),
(52110, 52, 'Buesaco'),
(52240, 52, 'Chachagüí'),
(52203, 52, 'Colón'),
(52207, 52, 'Consacá'),
(52210, 52, 'Contadero'),
(52215, 52, 'Córdoba'),
(52224, 52, 'Cuaspud Carlosama'),
(52227, 52, 'Cumbal'),
(52233, 52, 'Cumbitara'),
(52250, 52, 'El Charco'),
(52254, 52, 'El Peñol'),
(52256, 52, 'El Rosario'),
(52258, 52, 'El Tablón de Gómez'),
(52260, 52, 'El Tambo'),
(52520, 52, 'Francisco Pizarro'),
(52287, 52, 'Funes'),
(52317, 52, 'Guachucal'),
(52320, 52, 'Guaitarilla'),
(52323, 52, 'Gualmatán'),
(52352, 52, 'Iles'),
(52354, 52, 'Imués'),
(52356, 52, 'Ipiales'),
(52378, 52, 'La Cruz'),
(52381, 52, 'La Florida'),
(52385, 52, 'La Llanada'),
(52390, 52, 'La Tola'),
(52399, 52, 'La Unión'),
(52405, 52, 'Leiva'),
(52411, 52, 'Linares'),
(52418, 52, 'Los Andes'),
(52427, 52, 'Magüí'),
(52435, 52, 'Mallama'),
(52473, 52, 'Mosquera'),
(52480, 52, 'Nariño'),
(52490, 52, 'Olaya Herrera'),
(52506, 52, 'Ospina'),
(52001, 52, 'Pasto'),
(52540, 52, 'Policarpa'),
(52560, 52, 'Potosí'),
(52565, 52, 'Providencia'),
(52573, 52, 'Puerres'),
(52585, 52, 'Pupiales'),
(52612, 52, 'Ricaurte'),
(52621, 52, 'Roberto Payán'),
(52678, 52, 'Samaniego'),
(52835, 52, 'San Andrés de Tumaco'),
(52685, 52, 'San Bernardo'),
(52687, 52, 'San Lorenzo'),
(52693, 52, 'San Pablo'),
(52694, 52, 'San Pedro de Cartago'),
(52683, 52, 'Sandoná'),
(52696, 52, 'Santa Bárbara'),
(52699, 52, 'Santacruz'),
(52720, 52, 'Sapuyes'),
(52786, 52, 'Taminango'),
(52788, 52, 'Tangua'),
(52838, 52, 'Túquerres'),
(52885, 52, 'Yacuanquer'),
(54003, 54, 'Ábrego'),
(54051, 54, 'Arboledas'),
(54099, 54, 'Bochalema'),
(54109, 54, 'Bucarasica'),
(54128, 54, 'Cáchira'),
(54125, 54, 'Cácota'),
(54172, 54, 'Chinácota'),
(54174, 54, 'Chitagá'),
(54206, 54, 'Convención'),
(54223, 54, 'Cucutilla'),
(54239, 54, 'Durania'),
(54245, 54, 'El Carmen'),
(54250, 54, 'El Tarra'),
(54261, 54, 'El Zulia'),
(54313, 54, 'Gramalote'),
(54344, 54, 'Hacarí'),
(54347, 54, 'Herrán'),
(54385, 54, 'La Esperanza'),
(54398, 54, 'La Playa'),
(54377, 54, 'Labateca'),
(54405, 54, 'Los Patios'),
(54418, 54, 'Lourdes'),
(54480, 54, 'Mutiscua'),
(54498, 54, 'Ocaña'),
(54518, 54, 'Pamplona'),
(54520, 54, 'Pamplonita'),
(54553, 54, 'Puerto Santander'),
(54599, 54, 'Ragonvalia'),
(54660, 54, 'Salazar'),
(54670, 54, 'San Calixto'),
(54673, 54, 'San Cayetano'),
(54001, 54, 'San José de Cúcuta'),
(54680, 54, 'Santiago'),
(54720, 54, 'Sardinata'),
(54743, 54, 'Silos'),
(54800, 54, 'Teorama'),
(54810, 54, 'Tibú'),
(54820, 54, 'Toledo'),
(54871, 54, 'Villa Caro'),
(54874, 54, 'Villa del Rosario'),
(63001, 63, 'Armenia'),
(63111, 63, 'Buenavista'),
(63130, 63, 'Calarcá'),
(63190, 63, 'Circasia'),
(63212, 63, 'Córdoba'),
(63272, 63, 'Filandia'),
(63302, 63, 'Génova'),
(63401, 63, 'La Tebaida'),
(63470, 63, 'Montenegro'),
(63548, 63, 'Pijao'),
(63594, 63, 'Quimbaya'),
(63690, 63, 'Salento'),
(66045, 66, 'Apía'),
(66075, 66, 'Balboa'),
(66088, 66, 'Belén de Umbría'),
(66170, 66, 'Dosquebradas'),
(66318, 66, 'Guática'),
(66383, 66, 'La Celia'),
(66400, 66, 'La Virginia'),
(66440, 66, 'Marsella'),
(66456, 66, 'Mistrató'),
(66001, 66, 'Pereira'),
(66572, 66, 'Pueblo Rico'),
(66594, 66, 'Quinchía'),
(66682, 66, 'Santa Rosa de Cabal'),
(66687, 66, 'Santuario'),
(68013, 68, 'Aguada'),
(68020, 68, 'Albania'),
(68051, 68, 'Aratoca'),
(68077, 68, 'Barbosa'),
(68079, 68, 'Barichara'),
(68081, 68, 'Barrancabermeja'),
(68092, 68, 'Betulia'),
(68101, 68, 'Bolívar'),
(68001, 68, 'Bucaramanga'),
(68121, 68, 'Cabrera'),
(68132, 68, 'California'),
(68147, 68, 'Capitanejo'),
(68152, 68, 'Carcasí'),
(68160, 68, 'Cepitá'),
(68162, 68, 'Cerrito'),
(68167, 68, 'Charalá'),
(68169, 68, 'Charta'),
(68176, 68, 'Chima'),
(68179, 68, 'Chipatá'),
(68190, 68, 'Cimitarra'),
(68207, 68, 'Concepción'),
(68209, 68, 'Confines'),
(68211, 68, 'Contratación'),
(68217, 68, 'Coromoro'),
(68229, 68, 'Curití'),
(68235, 68, 'El Carmen de Chucurí'),
(68245, 68, 'El Guacamayo'),
(68250, 68, 'El Peñón'),
(68255, 68, 'El Playón'),
(68264, 68, 'Encino'),
(68266, 68, 'Enciso'),
(68271, 68, 'Florián'),
(68276, 68, 'Floridablanca'),
(68296, 68, 'Galán'),
(68298, 68, 'Gámbita'),
(68307, 68, 'Girón'),
(68318, 68, 'Guaca'),
(68320, 68, 'Guadalupe'),
(68322, 68, 'Guapotá'),
(68324, 68, 'Guavatá'),
(68327, 68, 'Güepsa'),
(68344, 68, 'Hato'),
(68368, 68, 'Jesús María'),
(68370, 68, 'Jordán'),
(68377, 68, 'La Belleza'),
(68397, 68, 'La Paz'),
(68385, 68, 'Landázuri'),
(68406, 68, 'Lebrija'),
(68418, 68, 'Los Santos'),
(68425, 68, 'Macaravita'),
(68432, 68, 'Málaga'),
(68444, 68, 'Matanza'),
(68464, 68, 'Mogotes'),
(68468, 68, 'Molagavita'),
(68498, 68, 'Ocamonte'),
(68500, 68, 'Oiba'),
(68502, 68, 'Onzaga'),
(68522, 68, 'Palmar'),
(68524, 68, 'Palmas del Socorro'),
(68533, 68, 'Páramo'),
(68547, 68, 'Piedecuesta'),
(68549, 68, 'Pinchote'),
(68572, 68, 'Puente Nacional'),
(68573, 68, 'Puerto Parra'),
(68575, 68, 'Puerto Wilches'),
(68615, 68, 'Rionegro'),
(68655, 68, 'Sabana de Torres'),
(68669, 68, 'San Andrés'),
(68673, 68, 'San Benito'),
(68679, 68, 'San Gil'),
(68682, 68, 'San Joaquín'),
(68684, 68, 'San José de Miranda'),
(68686, 68, 'San Miguel'),
(68689, 68, 'San Vicente de Chucurí'),
(68705, 68, 'Santa Bárbara'),
(68720, 68, 'Santa Helena del Opón'),
(68745, 68, 'Simacota'),
(68755, 68, 'Socorro'),
(68770, 68, 'Suaita'),
(68773, 68, 'Sucre'),
(68780, 68, 'Suratá'),
(68820, 68, 'Tona'),
(68855, 68, 'Valle de San José'),
(68861, 68, 'Vélez'),
(68867, 68, 'Vetas'),
(68872, 68, 'Villanueva'),
(68895, 68, 'Zapatoca'),
(70110, 70, 'Buenavista'),
(70124, 70, 'Caimito'),
(70230, 70, 'Chalán'),
(70204, 70, 'Colosó'),
(70215, 70, 'Corozal'),
(70221, 70, 'Coveñas'),
(70233, 70, 'El Roble'),
(70235, 70, 'Galeras'),
(70265, 70, 'Guaranda'),
(70400, 70, 'La Unión'),
(70418, 70, 'Los Palmitos'),
(70429, 70, 'Majagual'),
(70473, 70, 'Morroa'),
(70508, 70, 'Ovejas'),
(70523, 70, 'Palmito'),
(70670, 70, 'Sampués'),
(70678, 70, 'San Benito Abad'),
(70823, 70, 'San José de Toluviejo'),
(70702, 70, 'San Juan de Betulia'),
(70742, 70, 'San Luis de Sincé'),
(70708, 70, 'San Marcos'),
(70713, 70, 'San Onofre'),
(70717, 70, 'San Pedro'),
(70820, 70, 'Santiago de Tolú'),
(70001, 70, 'Sincelejo'),
(70771, 70, 'Sucre'),
(73024, 73, 'Alpujarra'),
(73026, 73, 'Alvarado'),
(73030, 73, 'Ambalema'),
(73043, 73, 'Anzoátegui'),
(73055, 73, 'Armero'),
(73067, 73, 'Ataco'),
(73124, 73, 'Cajamarca'),
(73148, 73, 'Carmen de Apicalá'),
(73152, 73, 'Casabianca'),
(73168, 73, 'Chaparral'),
(73200, 73, 'Coello'),
(73217, 73, 'Coyaima'),
(73226, 73, 'Cunday'),
(73236, 73, 'Dolores'),
(73268, 73, 'Espinal'),
(73270, 73, 'Falan'),
(73275, 73, 'Flandes'),
(73283, 73, 'Fresno'),
(73319, 73, 'Guamo'),
(73347, 73, 'Herveo'),
(73349, 73, 'Honda'),
(73001, 73, 'Ibagué'),
(73352, 73, 'Icononzo'),
(73408, 73, 'Lérida'),
(73411, 73, 'Líbano'),
(73449, 73, 'Melgar'),
(73461, 73, 'Murillo'),
(73483, 73, 'Natagaima'),
(73504, 73, 'Ortega'),
(73520, 73, 'Palocabildo'),
(73547, 73, 'Piedras'),
(73555, 73, 'Planadas'),
(73563, 73, 'Prado'),
(73585, 73, 'Purificación'),
(73616, 73, 'Rioblanco'),
(73622, 73, 'Roncesvalles'),
(73624, 73, 'Rovira'),
(73671, 73, 'Saldaña'),
(73675, 73, 'San Antonio'),
(73678, 73, 'San Luis'),
(73443, 73, 'San Sebastián de Mariquita'),
(73686, 73, 'Santa Isabel'),
(73770, 73, 'Suárez'),
(73854, 73, 'Valle de San Juan'),
(73861, 73, 'Venadillo'),
(73870, 73, 'Villahermosa'),
(73873, 73, 'Villarrica'),
(76020, 76, 'Alcalá'),
(76036, 76, 'Andalucía'),
(76041, 76, 'Ansermanuevo'),
(76054, 76, 'Argelia'),
(76100, 76, 'Bolívar'),
(76109, 76, 'Buenaventura'),
(76113, 76, 'Bugalagrande'),
(76122, 76, 'Caicedonia'),
(76126, 76, 'Calima'),
(76130, 76, 'Candelaria'),
(76147, 76, 'Cartago'),
(76233, 76, 'Dagua'),
(76243, 76, 'El Águila'),
(76246, 76, 'El Cairo'),
(76248, 76, 'El Cerrito'),
(76250, 76, 'El Dovio'),
(76275, 76, 'Florida'),
(76306, 76, 'Ginebra'),
(76318, 76, 'Guacarí'),
(76111, 76, 'Guadalajara de Buga'),
(76364, 76, 'Jamundí'),
(76377, 76, 'La Cumbre'),
(76400, 76, 'La Unión'),
(76403, 76, 'La Victoria'),
(76497, 76, 'Obando'),
(76520, 76, 'Palmira'),
(76563, 76, 'Pradera'),
(76606, 76, 'Restrepo'),
(76616, 76, 'Riofrío'),
(76622, 76, 'Roldanillo'),
(76670, 76, 'San Pedro'),
(76001, 76, 'Santiago de Cali'),
(76736, 76, 'Sevilla'),
(76823, 76, 'Toro'),
(76828, 76, 'Trujillo'),
(76834, 76, 'Tuluá'),
(76845, 76, 'Ulloa'),
(76863, 76, 'Versalles'),
(76869, 76, 'Vijes'),
(76890, 76, 'Yotoco'),
(76892, 76, 'Yumbo'),
(76895, 76, 'Zarzal'),
(81001, 81, 'Arauca'),
(81065, 81, 'Arauquita'),
(81220, 81, 'Cravo Norte'),
(81300, 81, 'Fortul'),
(81591, 81, 'Puerto Rondón'),
(81736, 81, 'Saravena'),
(81794, 81, 'Tame'),
(85010, 85, 'Aguazul'),
(85015, 85, 'Chámeza'),
(85125, 85, 'Hato Corozal'),
(85136, 85, 'La Salina'),
(85139, 85, 'Maní'),
(85162, 85, 'Monterrey'),
(85225, 85, 'Nunchía'),
(85230, 85, 'Orocué'),
(85250, 85, 'Paz de Ariporo'),
(85263, 85, 'Pore'),
(85279, 85, 'Recetor'),
(85300, 85, 'Sabanalarga'),
(85315, 85, 'Sácama'),
(85325, 85, 'San Luis de Palenque'),
(85400, 85, 'Támara'),
(85410, 85, 'Tauramena'),
(85430, 85, 'Trinidad'),
(85440, 85, 'Villanueva'),
(85001, 85, 'Yopal'),
(86219, 86, 'Colón'),
(86001, 86, 'Mocoa'),
(86320, 86, 'Orito'),
(86568, 86, 'Puerto Asís'),
(86569, 86, 'Puerto Caicedo'),
(86571, 86, 'Puerto Guzmán'),
(86573, 86, 'Puerto Leguízamo'),
(86755, 86, 'San Francisco'),
(86757, 86, 'San Miguel'),
(86760, 86, 'Santiago'),
(86749, 86, 'Sibundoy'),
(86865, 86, 'Valle del Guamuez'),
(86885, 86, 'Villagarzón'),
(88564, 88, 'Providencia'),
(88001, 88, 'San Andrés'),
(91263, 91, 'El Encanto'),
(91405, 91, 'La Chorrera'),
(91407, 91, 'La Pedrera'),
(91430, 91, 'La Victoria'),
(91001, 91, 'Leticia'),
(91460, 91, 'Mirití - Paraná'),
(91530, 91, 'Puerto Alegría'),
(91536, 91, 'Puerto Arica'),
(91540, 91, 'Puerto Nariño'),
(91669, 91, 'Puerto Santander'),
(91798, 91, 'Tarapacá'),
(94343, 94, 'Barrancominas'),
(94886, 94, 'Cacahual'),
(94001, 94, 'Inírida'),
(94885, 94, 'La Guadalupe'),
(94888, 94, 'Morichal'),
(94887, 94, 'Pana Pana'),
(94884, 94, 'Puerto Colombia'),
(94883, 94, 'San Felipe'),
(95015, 95, 'Calamar'),
(95025, 95, 'El Retorno'),
(95200, 95, 'Miraflores'),
(95001, 95, 'San José del Guaviare'),
(97161, 97, 'Carurú'),
(97001, 97, 'Mitú'),
(97511, 97, 'Pacoa'),
(97777, 97, 'Papunahua'),
(97666, 97, 'Taraira'),
(97889, 97, 'Yavaraté'),
(99773, 99, 'Cumaribo'),
(99524, 99, 'La Primavera'),
(99001, 99, 'Puerto Carreño'),
(99624, 99, 'Santa Rosalía');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `notificaciones`
--

CREATE TABLE `notificaciones` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `mensaje` text NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `leida` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `notificaciones`
--

INSERT INTO `notificaciones` (`id`, `usuario_id`, `mensaje`, `fecha`, `leida`) VALUES
(1, 2, 'Tienes una nueva solicitud de cita pendiente.', '2026-09-21 14:27:54', 0),
(2, 8, 'La cita #5 fue marcada como Aceptada.', '2026-09-21 14:28:06', 0),
(3, 8, 'La cita #5 fue marcada como Completada.', '2026-09-21 14:28:09', 0),
(4, 8, 'Tienes una nueva solicitud de cita pendiente.', '2026-09-21 15:19:45', 0),
(5, 10, 'La cita #6 fue marcada como Aceptada.', '2026-09-21 15:19:59', 0),
(6, 2, 'Tienes una nueva solicitud de cita pendiente.', '2026-09-21 15:47:52', 0),
(7, 2, 'Tienes una nueva solicitud de cita pendiente.', '2026-09-21 15:48:11', 0),
(8, 8, 'Tienes una nueva solicitud de cita pendiente.', '2026-09-21 15:49:26', 0),
(9, 2, 'Tienes una nueva solicitud de cita pendiente.', '2026-09-21 15:50:29', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `password_resets`
--

CREATE TABLE `password_resets` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `token_hash` char(64) NOT NULL,
  `expira_en` datetime NOT NULL,
  `usado_en` datetime DEFAULT NULL,
  `creado_en` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `password_resets`
--

INSERT INTO `password_resets` (`id`, `usuario_id`, `token_hash`, `expira_en`, `usado_en`, `creado_en`) VALUES
(1, 8, 'a762fca1218ec2b85d214a16152847509bc1eb0121939baa42c27929dffc8a22', '2026-09-21 09:06:30', '2026-09-21 09:10:56', '2026-09-21 13:36:30'),
(2, 8, '774051c60131ffbf6a1a050c4cb79343c119ebbc19b95b75f02d18f5b3d5b652', '2026-09-21 09:18:58', '2026-09-21 09:10:56', '2026-09-21 13:48:58'),
(3, 9, '3b34a85fe353a01ea8029dc29139d421efd10a07917a81ae5fc26ad6cd206c28', '2026-09-21 09:30:30', '2026-09-21 09:06:23', '2026-09-21 14:00:30'),
(4, 9, '4cf47a6ce0553a418fa092a299b308365a36de1901ee8e17f1a58cc49736fb20', '2026-09-21 09:35:12', '2026-09-21 09:06:23', '2026-09-21 14:05:12'),
(5, 8, '934dfb9001156b02fbd726c07987b30ed459deb601c6c1b455a0809559d791a0', '2026-09-21 09:37:18', '2026-09-21 09:10:56', '2026-09-21 14:07:18'),
(6, 9, '28b79a643b776bad7c0a4983677f9f41eac63c41d2c90becca6f7416b2eb0677', '2026-09-21 10:52:53', '2026-09-21 10:23:24', '2026-09-21 15:22:53'),
(7, 10, 'f933db3149dc1fe57907b8ac4a4304cccb76170edcbc0bf7a39d00efbee69c5c', '2026-09-21 10:54:08', NULL, '2026-09-21 15:24:08');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pedidos`
--

CREATE TABLE `pedidos` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `fecha_pedido` timestamp NOT NULL DEFAULT current_timestamp(),
  `estado` enum('Pendiente','Aceptado','Rechazado','Completado','Cancelado') DEFAULT 'Pendiente',
  `total` decimal(10,2) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `pedidos`
--

INSERT INTO `pedidos` (`id`, `usuario_id`, `fecha_pedido`, `estado`, `total`) VALUES
(1, 4, '2026-10-27 14:16:39', 'Completado', 148000.00),
(2, 3, '2026-09-02 14:16:39', 'Completado', 220000.00),
(3, 4, '2026-09-09 14:16:39', 'Completado', 54400.00),
(4, 7, '2026-09-11 14:16:39', 'Aceptado', 273000.00),
(5, 6, '2026-09-14 14:16:39', 'Completado', 80000.00),
(6, 7, '2026-09-07 14:16:39', 'Rechazado', 50000.00),
(7, 3, '2026-09-21 13:22:10', 'Cancelado', 4000000.00),
(8, 8, '2026-09-21 14:20:22', 'Completado', 1100000.00),
(9, 8, '2026-09-21 15:17:20', 'Cancelado', 6500000.00),
(10, 8, '2026-09-21 15:18:00', 'Completado', 13000000.00),
(11, 8, '2026-09-21 15:41:00', 'Completado', 16000000.00),
(12, 8, '2026-09-21 15:55:53', 'Completado', 27200000.00),
(13, 8, '2026-09-21 15:56:35', 'Completado', 8000000.00),
(14, 8, '2026-09-21 15:59:05', 'Completado', 5600000.00),
(15, 8, '2026-09-21 16:00:51', 'Pendiente', 4800000.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `productos`
--

CREATE TABLE `productos` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `categoria_id` int(11) DEFAULT NULL,
  `descripcion` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `productos`
--

INSERT INTO `productos` (`id`, `nombre`, `categoria_id`, `descripcion`) VALUES
(1, 'Café Especial', 3, 'Café de altura, secado al sol.'),
(2, 'Manzana Roja', 1, 'Manzanas frescas del Huila.'),
(3, 'Papa Criolla', 5, 'Papa de excelente calidad.'),
(4, 'Mango Tommy', 1, 'Mango Tommy maduro, calibre grande, ideal para exportación.'),
(5, 'Naranja Valencia', 1, 'Naranjas jugosas recién cosechadas, sin químicos.'),
(6, 'Espinaca', 2, 'Espinaca fresca cosechada el mismo día de entrega.'),
(7, 'Zanahoria', 3, 'Zanahoria fresca lavada y clasificada por tamaño.'),
(8, 'Tomate Chonto', 3, 'Tomate chonto rojo, cultivado bajo invernadero.'),
(9, 'Papa Pastusa', 4, 'Papa pastusa lavada, ideal para consumo y venta al detal.'),
(10, 'Yuca', 4, 'Yuca de buena calidad, tamaño uniforme.'),
(11, 'Fríjol Cargamanto', 5, 'Fríjol cargamanto seco, seleccionado a mano.'),
(12, 'Garbanzo', 5, 'Garbanzo seco de cosecha reciente, libre de impurezas.'),
(13, 'Maíz Amarillo', 6, 'Maíz amarillo trillado, apto para consumo animal y humano.'),
(14, 'Arroz Blanco', 6, 'Arroz blanco de primera calidad, grano largo.'),
(15, 'Café Pergamino', 7, 'Café pergamino seco cultivado a más de 1700 msnm.'),
(16, 'Café Tostado Premium', 7, 'Café tostado artesanalmente, notas achocolatadas.'),
(17, 'Cacao en Grano', 8, 'Cacao fermentado y secado al sol, listo para procesar.'),
(18, 'Rosas Rojas', 9, 'Rosas rojas de tallo largo, recién cortadas.'),
(19, 'Claveles', 9, 'Claveles de colores surtidos, cultivados en sabana.'),
(20, 'Suculentas', 10, 'Suculentas variadas listas para venta en vivero.'),
(21, 'Albahaca', 11, 'Albahaca fresca cortada, ideal para cocina y aromaterapia.'),
(22, 'Cilantro', 11, 'Cilantro fresco cosechado a diario en huerta propia.'),
(23, 'Almendras', 12, 'Almendras naturales, sin sal ni conservantes.'),
(24, 'Nueces', 12, 'Nueces de nogal criollo, cosecha de temporada.'),
(25, 'Queso Campesino', 13, 'Queso campesino elaborado el mismo día, sabor suave.'),
(26, 'Leche Fresca', 13, 'Leche fresca de vaca, entera y sin procesar.'),
(27, 'Huevos AA', 14, 'Huevos frescos de gallinas criadas en campo abierto.'),
(28, 'Pollo Campestre', 15, 'Pollo campestre criado en libertad, carne firme.'),
(29, 'Miel de Abejas', 16, 'Miel de abejas pura, sin procesar ni mezclar.'),
(30, 'Trucha Arcoíris', 17, 'Trucha arcoíris de criadero, entera y fresca.'),
(31, 'Semillas de Girasol', 18, 'Semillas de girasol seleccionadas para siembra.'),
(32, 'Pimienta Negra', 19, 'Pimienta negra en grano, secada tradicionalmente.'),
(33, 'Compost Orgánico', 20, 'Compost orgánico 100% natural, mejora la fertilidad del suelo.'),
(34, 'Pollo', 15, 'Pollo campestre criado en libertad, carne firme.'),
(35, 'Café', 7, 'De buena calidad'),
(36, 'Papa', 4, '');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `publicaciones`
--

CREATE TABLE `publicaciones` (
  `id` int(11) NOT NULL,
  `campesino_id` int(11) NOT NULL,
  `producto_id` int(11) NOT NULL,
  `titulo` varchar(255) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `precio_empresa` decimal(10,2) NOT NULL DEFAULT 0.00,
  `precio_comerciante` decimal(10,2) NOT NULL DEFAULT 0.00,
  `cantidad_disponible` float NOT NULL,
  `unidad_medida` varchar(20) DEFAULT NULL,
  `imagen` varchar(255) DEFAULT NULL,
  `transporte` tinyint(1) NOT NULL DEFAULT 0,
  `fecha_publicacion` timestamp NOT NULL DEFAULT current_timestamp(),
  `estado` enum('Activa','Inactiva','Agotada') DEFAULT 'Activa'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `publicaciones`
--

INSERT INTO `publicaciones` (`id`, `campesino_id`, `producto_id`, `titulo`, `descripcion`, `precio_empresa`, `precio_comerciante`, `cantidad_disponible`, `unidad_medida`, `imagen`, `transporte`, `fecha_publicacion`, `estado`) VALUES
(2, 1, 2, 'Manzana Roja', 'Cosecha fresca de temporada.', 5000.00, 5000.00, 70, 'Libras (lb)', 'uploads/Manzana_Roja.jpg', 0, '2026-09-08 12:52:53', 'Activa'),
(3, 1, 4, 'Mango Tommy', 'Mango Tommy maduro, calibre grande, ideal para exportación.', 3200.00, 3200.00, 260, 'Kilogramos (kg)', 'uploads/Mango_Tommy.jpg', 1, '2026-09-08 12:53:29', 'Activa'),
(4, 1, 5, 'Naranja Valencia', 'Naranjas jugosas recién cosechadas, sin químicos.', 1800.00, 1800.00, 500, 'Kilogramos (kg)', 'uploads/Naranja_Valencia.jpg', 1, '2026-09-08 12:53:30', 'Activa'),
(5, 1, 6, 'Espinaca', 'Espinaca fresca cosechada el mismo día de entrega.', 2500.00, 2500.00, 80, 'Kilogramos (kg)', 'uploads/Espinaca.jpg', 0, '2026-09-08 12:53:32', 'Activa'),
(6, 1, 7, 'Zanahoria', 'Zanahoria fresca lavada y clasificada por tamaño.', 1600.00, 1600.00, 400, 'Kilogramos (kg)', 'uploads/Zanahoria.png', 1, '2026-09-08 12:53:34', 'Activa'),
(7, 1, 8, 'Tomate Chonto', 'Tomate chonto rojo, cultivado bajo invernadero.', 2200.00, 2200.00, 350, 'Kilogramos (kg)', 'uploads/Tomate_chonto.jpg', 1, '2026-09-08 12:53:35', 'Activa'),
(8, 1, 9, 'Papa Pastusa', 'Papa pastusa lavada, ideal para consumo y venta al detal.', 1900.00, 1900.00, 800, 'Bultos', 'uploads/Papa_Pastusa.jpg', 1, '2026-09-08 12:53:36', 'Activa'),
(9, 1, 10, 'Yuca', 'Yuca de buena calidad, tamaño uniforme.', 1500.00, 1500.00, 600, 'Bultos', 'uploads/Yuca.jpg', 0, '2026-09-08 12:53:36', 'Activa'),
(10, 1, 11, 'Fríjol Cargamanto', 'Fríjol cargamanto seco, seleccionado a mano.', 6800.00, 6800.00, 192, 'Kilogramos (kg)', 'uploads/Frijol_Cargamanto.png', 1, '2026-09-08 12:53:36', 'Activa'),
(11, 1, 12, 'Garbanzo', 'Garbanzo seco de cosecha reciente, libre de impurezas.', 7200.00, 7200.00, 150, 'Kilogramos (kg)', 'uploads/Garbanzo.jpg', 0, '2026-09-08 12:53:37', 'Activa'),
(12, 1, 13, 'Maíz Amarillo', 'Maíz amarillo trillado, apto para consumo animal y humano.', 1700.00, 1700.00, 1000, 'Bultos', 'uploads/Maiz_Amarillo.png', 1, '2026-09-08 12:53:37', 'Activa'),
(13, 1, 14, 'Arroz Blanco', 'Arroz blanco de primera calidad, grano largo.', 3200.00, 3200.00, 700, 'Bultos', 'uploads/Arroz_Blanco.webp', 1, '2026-09-08 12:53:37', 'Activa'),
(14, 1, 15, 'Café Pergamino', 'Café pergamino seco cultivado a más de 1700 msnm.', 800000.00, 15500.00, 400, 'Arrobas', 'uploads/Cafe_Pergamino.webp', 1, '2026-09-08 12:53:38', 'Activa'),
(15, 1, 16, 'Café Tostado Premium', 'Café tostado artesanalmente, notas achocolatadas.', 22000.00, 22000.00, 40, 'Kilogramos (kg)', 'uploads/Cafe_Tostado_Premium.webp', 0, '2026-09-08 12:53:38', 'Activa'),
(16, 1, 17, 'Cacao en Grano', 'Cacao fermentado y secado al sol, listo para procesar.', 13500.00, 13500.00, 250, 'Kilogramos (kg)', 'uploads/Cacao_en_Grano.jpg', 1, '2026-09-08 12:53:38', 'Activa'),
(17, 1, 18, 'Rosas Rojas', 'Rosas rojas de tallo largo, recién cortadas.', 900.00, 900.00, 1200, 'Docenas', 'uploads/Rosas.jpg', 1, '2026-09-08 12:53:39', 'Activa'),
(18, 2, 19, 'Claveles', 'Claveles de colores surtidos, cultivados en sabana.', 700.00, 700.00, 1500, 'Docenas', 'uploads/Claveles.jpg', 0, '2026-09-08 12:53:39', 'Activa'),
(19, 2, 20, 'Suculentas', 'Suculentas variadas listas para venta en vivero.', 4500.00, 4500.00, 250, 'Unidades', 'uploads/Suculentas.jpg', 0, '2026-09-08 12:53:39', 'Activa'),
(20, 2, 21, 'Albahaca', 'Albahaca fresca cortada, ideal para cocina y aromaterapia.', 2000.00, 2000.00, 120, 'Unidades', 'uploads/Albahaca.jpg', 0, '2026-09-08 12:53:40', 'Activa'),
(21, 2, 22, 'Cilantro', 'Cilantro fresco cosechado a diario en huerta propia.', 1200.00, 1200.00, 200, 'Unidades', 'uploads/Cilantro.jpg', 0, '2026-09-08 12:53:40', 'Activa'),
(22, 2, 23, 'Almendras', 'Almendras naturales, sin sal ni conservantes.', 28000.00, 28000.00, 60, 'Kilogramos (kg)', 'uploads/Almendras.jpeg', 1, '2026-09-08 12:53:40', 'Activa'),
(23, 2, 24, 'Nueces', 'Nueces de nogal criollo, cosecha de temporada.', 32000.00, 32000.00, 45, 'Kilogramos (kg)', 'uploads/Nueces.jpg', 0, '2026-09-08 12:53:41', 'Activa'),
(24, 2, 25, 'Queso Campesino', 'Queso campesino elaborado el mismo día, sabor suave.', 14500.00, 14500.00, 78, 'Kilogramos (kg)', 'uploads/Queso_Campesino.jpg', 1, '2026-09-08 12:53:41', 'Activa'),
(25, 2, 26, 'Leche Fresca', 'Leche fresca de vaca, entera y sin procesar.', 2600.00, 2600.00, 300, 'Litros', 'uploads/Leche_Fresca.jpg', 1, '2026-09-08 12:53:41', 'Activa'),
(26, 2, 27, 'Huevos AA', 'Huevos frescos de gallinas criadas en campo abierto.', 13000.00, 13000.00, 150, 'Docenas', 'uploads/Huevos_AA.jpg', 1, '2026-09-08 12:53:42', 'Activa'),
(27, 2, 34, 'Pollo', 'Pollo campestre criado en libertad, carne firme.', 11500.00, 11500.00, 80, 'Unidades', 'uploads/Pollo.webp', 1, '2026-09-08 12:53:42', 'Activa'),
(28, 2, 29, 'Miel de Abejas', 'Miel de abejas pura, sin procesar ni mezclar.', 24000.00, 24000.00, 100, 'Litros', 'uploads/Miel_de_Abejas.jpg', 0, '2026-09-08 12:53:42', 'Activa'),
(29, 2, 30, 'Trucha Arcoíris', 'Trucha arcoíris de criadero, entera y fresca.', 16500.00, 16500.00, 64, 'Kilogramos (kg)', 'uploads/Trucha_Arcoiris.jpeg', 1, '2026-09-08 12:53:43', 'Activa'),
(30, 2, 31, 'Semillas de Girasol', 'Semillas de girasol seleccionadas para siembra.', 9500.00, 9500.00, 120, 'Kilogramos (kg)', 'uploads/Semillas_de_Girasol.jpg', 0, '2026-09-08 12:53:43', 'Activa'),
(31, 2, 32, 'Pimienta Negra', 'Pimienta negra en grano, secada tradicionalmente.', 26000.00, 26000.00, 50, 'Kilogramos (kg)', 'uploads/Pimienta_Negra.webp', 0, '2026-09-08 12:53:43', 'Activa'),
(32, 2, 33, 'Compost Orgánico', 'Compost orgánico 100% natural, mejora la fertilidad del suelo.', 8500.00, 8500.00, 200, 'Bultos', 'uploads/Compost_Organico_para_Cultivos.jpg', 1, '2026-09-08 12:53:44', 'Activa'),
(63, 3, 35, 'Café', 'De buena calidad', 300000.00, 320000.00, 5, 'Sacos', 'uploads/Manicomio_Bus_9_16.png', 1, '2026-09-21 15:14:19', 'Activa'),
(64, 3, 36, 'Papa', '', 80000.00, 70000.00, 0, 'Bultos', 'uploads/Procesion_Pagana_9_16.png', 1, '2026-09-21 15:58:53', 'Agotada');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `reseñas`
--

CREATE TABLE `reseñas` (
  `id` int(11) NOT NULL,
  `usuario_id` int(11) NOT NULL,
  `publicacion_id` int(11) NOT NULL,
  `calificacion` int(1) DEFAULT NULL CHECK (`calificacion` between 1 and 5),
  `comentario` text DEFAULT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `reseñas`
--

INSERT INTO `reseñas` (`id`, `usuario_id`, `publicacion_id`, `calificacion`, `comentario`, `fecha`) VALUES
(1, 4, 2, 5, 'Excelente calidad, siempre llega fresca y a tiempo.', '2026-09-14 14:16:39'),
(2, 3, 3, 4, 'Buen producto y entrega puntual, seguiremos comprando.', '2026-09-14 14:16:39'),
(3, 6, 15, 5, 'El mejor café que he comprado en la plataforma.', '2026-09-14 14:16:39'),
(4, 7, 24, 3, 'Buen sabor, pero el último pedido llegó con algo de retraso.', '2026-09-14 14:16:39');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

CREATE TABLE `roles` (
  `id` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `roles`
--

INSERT INTO `roles` (`id`, `nombre`) VALUES
(1, 'Administrador'),
(2, 'Campesino'),
(3, 'Empresa'),
(4, 'Comerciante');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `solicitudes`
--

CREATE TABLE `solicitudes` (
  `id` int(11) NOT NULL,
  `empresa_id` int(11) NOT NULL,
  `campesino_id` int(11) NOT NULL,
  `mensaje` text DEFAULT NULL,
  `fecha` timestamp NOT NULL DEFAULT current_timestamp(),
  `estado` enum('Pendiente','Respondida') DEFAULT 'Pendiente'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ubicaciones`
--

CREATE TABLE `ubicaciones` (
  `id` int(11) NOT NULL,
  `departamento` varchar(100) NOT NULL,
  `municipio` varchar(100) NOT NULL,
  `direccion` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `ubicaciones`
--

INSERT INTO `ubicaciones` (`id`, `departamento`, `municipio`, `direccion`) VALUES
(1, 'Cundinamarca', 'Bogota DC', 'Vereda El Triunfo'),
(2, 'Cundinamarca', 'Bogotá', 'Calle 100 #15-20'),
(3, 'Antioquia', 'Medellín', 'Carrera 45 #30-10'),
(4, 'Antioquia', 'Marinilla', 'Vereda La Esperanza'),
(5, 'Valle del Cauca', 'Cali', 'Zona Industrial Acopi'),
(6, 'Bogotá D.C.', 'Bogotá', 'Bogota'),
(7, 'Bogotá D.C.', 'Bogotá', 'Bogota'),
(8, 'Boyacá', 'Belén', 'La esperanza');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `rol_id` int(11) NOT NULL,
  `estado` enum('Activo','Inactivo') DEFAULT 'Activo',
  `fecha_registro` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`id`, `nombre`, `email`, `password`, `rol_id`, `estado`, `fecha_registro`) VALUES
(1, 'Admin CoAgrix', 'admin@coagrix.com', 'scrypt:32768:8:1$ryAuXyzdydGekDs6$e081c9a03d6c8545254bb15bf00072747fbcf817290d9a323548eb61c621acf4ee30b4b1a6cc0376b2cb2168b4f9911e7424e16f75897f13ab0ca7eace561c68', 1, 'Activo', '2026-09-08 12:52:53'),
(2, 'Juan Campesino', 'campesino@coagrix.com', 'scrypt:32768:8:1$GZegweEd4KaEn8sl$cd7c42cee1f4ecdbff1f7f9e2ed17a2ad2fd5de1f7c93e918a388c94b249dc76407a2fa47f8e0e83fee5ca5e85f35e7bd59a5991fc244c5ec9b5cf4b89839650', 2, 'Activo', '2026-09-08 12:52:53'),
(3, 'AgroExport S.A.S', 'empresa@coagrix.com', 'scrypt:32768:8:1$YmQxdpy1JP5NYdPT$58ada87624e75cb5fe98d1e4c8c65dd287e9c128ab329ee9fe1d1cec1cffca86250b897c9c26218839c440210ae462421d49676bcbb7facfc06012283606268e', 3, 'Activo', '2026-09-08 12:52:53'),
(4, 'Pedro Comerciante', 'comerciante@coagrix.com', 'scrypt:32768:8:1$CIF94nQQK3oJcUmh$b4869b97a206b1832882bbc001cbeb99a02b9cfb178292cc52ae8bc1df1b1ee53a65f5113166194667b8c0588490f747ec52879916d09a0af9b311df6c39f552', 4, 'Activo', '2026-09-08 12:52:53'),
(5, 'María Fernanda Rojas', 'mariarojas.campesina@coagrix.com', 'scrypt:32768:8:1$2JCSzx057vngv7dl$e26973e849e18432a97653a43f4d951584f9024d72c81adaf19ef8d91cf86cc1cec388ddf28a9ef28f424ada16732756efff9d1b41ddc392693107fe2f7dc54a', 2, 'Activo', '2026-09-08 12:53:27'),
(6, 'Laura Gómez', 'lauragomez.comerciante@coagrix.com', 'scrypt:32768:8:1$wVkUWSIferk43Ycw$00208cc256213385d0fe8e2781cfdbec33b3ffd2ae3b29583a1ce752c60f8f44beda04f6327216c4b3076eab57ce25ae0161c1c9995c26d4e5225697a1d389a6', 4, 'Activo', '2026-09-14 14:16:39'),
(7, 'Frutas del Valle S.A.S', 'frutasdelvalle@coagrix.com', 'scrypt:32768:8:1$xtNivKvKBOVc4HOF$257122c60633057ec3e5ae2f22936a3299bd1a92be6260b10330c0c92d74fbbbf1a335207630ac41696f6e9b80ebcacdd9b0b2f8b09f6ac42510a2595298bfba', 3, 'Activo', '2026-09-14 14:16:39'),
(8, 'felipe', 'davidfeliperodriguezl1604@gmail.com', 'scrypt:32768:8:1$zy18aUtwMAmI00DI$3161bebdd40c98768d9e637599cdbeb9c7afcdebdef2a26c0843ec7221c1db4f54f0f0b7b43f841f3dccde9cf3b5d5cfb40121ffbcf7eb7439343eaefcffd1d9', 4, 'Activo', '2026-09-21 13:35:50'),
(9, 'Andres', 'pinedatorresjuanandres@gmail.com', 'scrypt:32768:8:1$rmxk9p7p355U1nYv$bdc02bfa51f6356123de97562397a0fe67c87afa472568896b1ab0179e995db9e56c51931f187d0ff76e5a10a382626a5c9e6fd2a6a55836b153588afd99fbce', 4, 'Activo', '2026-09-21 14:00:13'),
(10, 'Uldarico', 'uldandra@gmail.com', 'scrypt:32768:8:1$H91l40BAFsID1VPN$5053f8afddadcd0a4617d75c19a31e9541d7dc9a5bd3db8a350c5a9977f01726ca72d7bbe427d395b5268df8a376612387ed1278b65b86b620cd32249ee9a211', 2, 'Activo', '2026-09-21 15:11:17');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `archivos`
--
ALTER TABLE `archivos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `publicacion_id` (`publicacion_id`);

--
-- Indices de la tabla `campesinos`
--
ALTER TABLE `campesinos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `ubicacion_id` (`ubicacion_id`);

--
-- Indices de la tabla `categorias`
--
ALTER TABLE `categorias`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_categoria_nombre` (`nombre`);

--
-- Indices de la tabla `citas`
--
ALTER TABLE `citas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_citas_solicitante` (`solicitante_id`),
  ADD KEY `idx_citas_receptor` (`receptor_id`),
  ADD KEY `idx_citas_fecha_hora` (`fecha`,`hora`);

--
-- Indices de la tabla `comentarios`
--
ALTER TABLE `comentarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_comentarios_usuario` (`usuario_id`);

--
-- Indices de la tabla `comerciantes`
--
ALTER TABLE `comerciantes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `ubicacion_id` (`ubicacion_id`);

--
-- Indices de la tabla `departamentos`
--
ALTER TABLE `departamentos`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_departamentos_nombre` (`nombre`);

--
-- Indices de la tabla `detalle_pedidos`
--
ALTER TABLE `detalle_pedidos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `pedido_id` (`pedido_id`),
  ADD KEY `idx_detalle_pedidos_publicacion_pedido` (`publicacion_id`,`pedido_id`);

--
-- Indices de la tabla `empresas`
--
ALTER TABLE `empresas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `ubicacion_id` (`ubicacion_id`);

--
-- Indices de la tabla `favoritos`
--
ALTER TABLE `favoritos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `publicacion_id` (`publicacion_id`);

--
-- Indices de la tabla `historial_precios`
--
ALTER TABLE `historial_precios`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_publicacion` (`publicacion_id`);

--
-- Indices de la tabla `mensajes`
--
ALTER TABLE `mensajes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `remitente_id` (`remitente_id`),
  ADD KEY `idx_mensajes_destinatario_leido_fecha` (`destinatario_id`,`leido`,`fecha`);

--
-- Indices de la tabla `municipios`
--
ALTER TABLE `municipios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_municipios_depto_nombre` (`departamento_id`,`nombre`);

--
-- Indices de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`);

--
-- Indices de la tabla `password_resets`
--
ALTER TABLE `password_resets`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_password_resets_token` (`token_hash`),
  ADD KEY `idx_password_resets_usuario` (`usuario_id`);

--
-- Indices de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_pedidos_usuario_estado_fecha` (`usuario_id`,`estado`,`fecha_pedido`);

--
-- Indices de la tabla `productos`
--
ALTER TABLE `productos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `categoria_id` (`categoria_id`);

--
-- Indices de la tabla `publicaciones`
--
ALTER TABLE `publicaciones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `producto_id` (`producto_id`),
  ADD KEY `idx_publicaciones_campesino_estado_fecha` (`campesino_id`,`estado`,`fecha_publicacion`);

--
-- Indices de la tabla `reseñas`
--
ALTER TABLE `reseñas`
  ADD PRIMARY KEY (`id`),
  ADD KEY `usuario_id` (`usuario_id`),
  ADD KEY `publicacion_id` (`publicacion_id`);

--
-- Indices de la tabla `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `solicitudes`
--
ALTER TABLE `solicitudes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `empresa_id` (`empresa_id`),
  ADD KEY `campesino_id` (`campesino_id`);

--
-- Indices de la tabla `ubicaciones`
--
ALTER TABLE `ubicaciones`
  ADD PRIMARY KEY (`id`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `rol_id` (`rol_id`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `archivos`
--
ALTER TABLE `archivos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=97;

--
-- AUTO_INCREMENT de la tabla `campesinos`
--
ALTER TABLE `campesinos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT de la tabla `categorias`
--
ALTER TABLE `categorias`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=47;

--
-- AUTO_INCREMENT de la tabla `citas`
--
ALTER TABLE `citas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT de la tabla `comentarios`
--
ALTER TABLE `comentarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT de la tabla `comerciantes`
--
ALTER TABLE `comerciantes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `detalle_pedidos`
--
ALTER TABLE `detalle_pedidos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=18;

--
-- AUTO_INCREMENT de la tabla `empresas`
--
ALTER TABLE `empresas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `favoritos`
--
ALTER TABLE `favoritos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `historial_precios`
--
ALTER TABLE `historial_precios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=156;

--
-- AUTO_INCREMENT de la tabla `mensajes`
--
ALTER TABLE `mensajes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=20;

--
-- AUTO_INCREMENT de la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de la tabla `password_resets`
--
ALTER TABLE `password_resets`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT de la tabla `pedidos`
--
ALTER TABLE `pedidos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT de la tabla `productos`
--
ALTER TABLE `productos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=37;

--
-- AUTO_INCREMENT de la tabla `publicaciones`
--
ALTER TABLE `publicaciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=65;

--
-- AUTO_INCREMENT de la tabla `reseñas`
--
ALTER TABLE `reseñas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `roles`
--
ALTER TABLE `roles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT de la tabla `solicitudes`
--
ALTER TABLE `solicitudes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `ubicaciones`
--
ALTER TABLE `ubicaciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `archivos`
--
ALTER TABLE `archivos`
  ADD CONSTRAINT `archivos_ibfk_1` FOREIGN KEY (`publicacion_id`) REFERENCES `publicaciones` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `campesinos`
--
ALTER TABLE `campesinos`
  ADD CONSTRAINT `campesinos_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `campesinos_ibfk_2` FOREIGN KEY (`ubicacion_id`) REFERENCES `ubicaciones` (`id`);

--
-- Filtros para la tabla `citas`
--
ALTER TABLE `citas`
  ADD CONSTRAINT `citas_ibfk_receptor` FOREIGN KEY (`receptor_id`) REFERENCES `usuarios` (`id`),
  ADD CONSTRAINT `citas_ibfk_solicitante` FOREIGN KEY (`solicitante_id`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `comentarios`
--
ALTER TABLE `comentarios`
  ADD CONSTRAINT `comentarios_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `comerciantes`
--
ALTER TABLE `comerciantes`
  ADD CONSTRAINT `comerciantes_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `comerciantes_ibfk_2` FOREIGN KEY (`ubicacion_id`) REFERENCES `ubicaciones` (`id`);

--
-- Filtros para la tabla `detalle_pedidos`
--
ALTER TABLE `detalle_pedidos`
  ADD CONSTRAINT `detalle_pedidos_ibfk_1` FOREIGN KEY (`pedido_id`) REFERENCES `pedidos` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `detalle_pedidos_ibfk_2` FOREIGN KEY (`publicacion_id`) REFERENCES `publicaciones` (`id`);

--
-- Filtros para la tabla `empresas`
--
ALTER TABLE `empresas`
  ADD CONSTRAINT `empresas_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `empresas_ibfk_2` FOREIGN KEY (`ubicacion_id`) REFERENCES `ubicaciones` (`id`);

--
-- Filtros para la tabla `favoritos`
--
ALTER TABLE `favoritos`
  ADD CONSTRAINT `favoritos_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  ADD CONSTRAINT `favoritos_ibfk_2` FOREIGN KEY (`publicacion_id`) REFERENCES `publicaciones` (`id`);

--
-- Filtros para la tabla `historial_precios`
--
ALTER TABLE `historial_precios`
  ADD CONSTRAINT `historial_precios_ibfk_1` FOREIGN KEY (`publicacion_id`) REFERENCES `publicaciones` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `mensajes`
--
ALTER TABLE `mensajes`
  ADD CONSTRAINT `mensajes_ibfk_1` FOREIGN KEY (`remitente_id`) REFERENCES `usuarios` (`id`),
  ADD CONSTRAINT `mensajes_ibfk_2` FOREIGN KEY (`destinatario_id`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `municipios`
--
ALTER TABLE `municipios`
  ADD CONSTRAINT `municipios_ibfk_1` FOREIGN KEY (`departamento_id`) REFERENCES `departamentos` (`id`);

--
-- Filtros para la tabla `notificaciones`
--
ALTER TABLE `notificaciones`
  ADD CONSTRAINT `notificaciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `password_resets`
--
ALTER TABLE `password_resets`
  ADD CONSTRAINT `password_resets_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE;

--
-- Filtros para la tabla `pedidos`
--
ALTER TABLE `pedidos`
  ADD CONSTRAINT `pedidos_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`);

--
-- Filtros para la tabla `productos`
--
ALTER TABLE `productos`
  ADD CONSTRAINT `productos_ibfk_1` FOREIGN KEY (`categoria_id`) REFERENCES `categorias` (`id`);

--
-- Filtros para la tabla `publicaciones`
--
ALTER TABLE `publicaciones`
  ADD CONSTRAINT `publicaciones_ibfk_1` FOREIGN KEY (`campesino_id`) REFERENCES `campesinos` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `publicaciones_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id`);

--
-- Filtros para la tabla `reseñas`
--
ALTER TABLE `reseñas`
  ADD CONSTRAINT `reseñas_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`),
  ADD CONSTRAINT `reseñas_ibfk_2` FOREIGN KEY (`publicacion_id`) REFERENCES `publicaciones` (`id`);

--
-- Filtros para la tabla `solicitudes`
--
ALTER TABLE `solicitudes`
  ADD CONSTRAINT `solicitudes_ibfk_1` FOREIGN KEY (`empresa_id`) REFERENCES `empresas` (`id`),
  ADD CONSTRAINT `solicitudes_ibfk_2` FOREIGN KEY (`campesino_id`) REFERENCES `campesinos` (`id`);

--
-- Filtros para la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
