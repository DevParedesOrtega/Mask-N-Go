-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 12-12-2025 a las 03:19:37
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
-- Base de datos: `maskngo`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `clientes`
--

CREATE TABLE `clientes` (
  `Id_cliente` int(11) NOT NULL COMMENT 'PK, Identificador unico',
  `Nombre` text NOT NULL COMMENT 'nombre (es)',
  `Apellido_Paterno` text NOT NULL COMMENT 'Apellido paterno del cleinte',
  `Telefono` varchar(255) NOT NULL COMMENT 'telefono de contacto',
  `Fecha_Registro` datetime DEFAULT current_timestamp() COMMENT 'Fecha de creacion',
  `Estado` enum('Activo','Bloqueado','Suspendido','Inactivo') NOT NULL DEFAULT 'Activo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `clientes`
--

INSERT INTO `clientes` (`Id_cliente`, `Nombre`, `Apellido_Paterno`, `Telefono`, `Fecha_Registro`, `Estado`) VALUES
(25, 'jorge', 'paredes', '6181478117', '2025-11-29 14:04:09', 'Inactivo'),
(31, 'maria gabriela', 'ortega', '61812345678', '2025-11-29 17:42:08', 'Activo'),
(44, 'Andrea', 'Garvalena', '618123456789', '2025-12-11 20:13:07', 'Activo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `configuracion`
--

CREATE TABLE `configuracion` (
  `Id_Config` int(11) NOT NULL,
  `Nombre_Config` varchar(100) NOT NULL,
  `Valor_Config` varchar(255) NOT NULL,
  `Descripcion` text DEFAULT NULL,
  `Fecha_Modificacion` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `configuracion`
--

INSERT INTO `configuracion` (`Id_Config`, `Nombre_Config`, `Valor_Config`, `Descripcion`, `Fecha_Modificacion`) VALUES
(1, 'PENALIZACION_DIA', '50.00', 'Monto de penalizaci?n por d?a de retraso en rentas', '2025-11-21 22:12:34'),
(2, 'PENALIZACIONDIA', '50.0', 'Monto de penalización por día de retraso en rentas', '2025-12-01 17:00:00');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_rentas`
--

CREATE TABLE `detalle_rentas` (
  `Id_DetalleRenta` int(11) NOT NULL COMMENT 'PK',
  `Id_Renta` int(11) NOT NULL COMMENT 'Referencia a la tabla de rentas',
  `Codigo_Barras` varchar(255) NOT NULL COMMENT 'Referencia a la tabla de inventario',
  `Cantidad` int(11) NOT NULL COMMENT 'Cantidad rentada',
  `Precio_Unitario` decimal(10,2) NOT NULL COMMENT 'dias por precio',
  `Subtotal` decimal(10,2) NOT NULL COMMENT 'Cantidad x precio x'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `detalle_rentas`
--

INSERT INTO `detalle_rentas` (`Id_DetalleRenta`, `Id_Renta`, `Codigo_Barras`, `Cantidad`, `Precio_Unitario`, `Subtotal`) VALUES
(22, 22, 'DISNEY0000', 1, 300.00, 600.00),
(46, 46, 'DISNEY0000', 1, 300.00, 600.00),
(47, 47, 'DISNEY0000', 1, 300.00, 1200.00),
(48, 48, 'DISNEY0000', 1, 300.00, 1500.00),
(49, 49, 'DISNEY0000', 1, 300.00, 600.00),
(50, 50, 'DISNEY0000', 1, 300.00, 1500.00),
(51, 51, 'DISNEY0000', 1, 300.00, 600.00),
(52, 52, 'DISNEY0000', 1, 300.00, 900.00),
(53, 53, 'DISNEY0003', 1, 250.00, 2500.00),
(54, 54, 'DISNEY0003', 1, 250.00, 2500.00),
(55, 55, 'DISNEY0004', 1, 380.00, 380.00),
(56, 56, 'DISNEY0000', 1, 300.00, 900.00),
(57, 57, 'DISNEY0000', 1, 300.00, 600.00),
(58, 58, 'DISNEY0000', 1, 300.00, 15000.00),
(59, 58, 'DISNEY0000', 1, 300.00, 15000.00),
(60, 59, 'DISNEY0000', 1, 300.00, 24000.00),
(61, 60, 'diseny0008', 1, 125.00, 625.00),
(62, 61, 'DISNEY0000', 1, 300.00, 30000.00),
(63, 61, 'DISNEY0004', 1, 380.00, 38000.00),
(64, 61, 'DISNEY0001', 1, 350.00, 35000.00),
(65, 61, 'DISNEY0003', 1, 250.00, 25000.00),
(66, 62, 'diseny0008', 1, 125.00, 625.00),
(67, 63, 'DISNEY0004', 1, 380.00, 1900.00),
(68, 64, 'DISNEY0000', 1, 300.00, 900.00),
(69, 64, 'DISNEY0000', 1, 300.00, 900.00),
(70, 65, 'DISNEY0004', 1, 380.00, 760.00),
(71, 65, 'diseny0008', 1, 125.00, 250.00),
(72, 66, 'diseny0008', 1, 125.00, 375.00),
(73, 67, 'diseny0008', 1, 125.00, 125.00),
(74, 68, 'DISNEY0000', 1, 300.00, 3000.00),
(75, 69, 'diseny0008', 1, 125.00, 6250.00),
(76, 69, 'diseny0008', 1, 125.00, 6250.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_ventas`
--

CREATE TABLE `detalle_ventas` (
  `ID_DetalleVenta` int(11) NOT NULL COMMENT 'PK',
  `Id_Venta` int(11) NOT NULL COMMENT 'Referencia a la tabla ventas',
  `Codigo_Barras` varchar(255) NOT NULL COMMENT 'Referencia a la tabla de inventario',
  `Cantidad` int(11) NOT NULL COMMENT 'Cantidad vendida',
  `Precio_Unitario` decimal(10,2) NOT NULL COMMENT 'Precio al momento de la venta',
  `Subtotal` decimal(10,2) NOT NULL COMMENT 'Cantidad x Precio_Unitario'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `detalle_ventas`
--

INSERT INTO `detalle_ventas` (`ID_DetalleVenta`, `Id_Venta`, `Codigo_Barras`, `Cantidad`, `Precio_Unitario`, `Subtotal`) VALUES
(15, 17, 'DISNEY0003', 1, 1850.00, 1850.00),
(16, 18, 'diseny0008', 1, 15500.00, 15500.00),
(17, 18, 'DISNEY0000', 1, 2000.00, 2000.00),
(18, 19, 'DISNEY0001', 1, 1500.00, 1500.00),
(19, 19, 'DISNEY0004', 1, 2500.00, 2500.00),
(20, 20, 'DISNEY0004', 1, 2500.00, 2500.00),
(21, 20, 'DISNEY0004', 1, 2500.00, 2500.00),
(22, 20, 'DISNEY0004', 1, 2500.00, 2500.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `inventario`
--

CREATE TABLE `inventario` (
  `Codigo_Barras` varchar(255) NOT NULL COMMENT 'PK, Codigo de articulo o ID',
  `Descripcion` text NOT NULL COMMENT 'Descripcion del articulo',
  `Talla` text NOT NULL COMMENT 'Talla (S,M,L,XL, UNI)',
  `Color` text DEFAULT NULL COMMENT 'Color principal del traje',
  `Categoria` text DEFAULT NULL COMMENT 'categorias (Superheroes, villanos, etc)',
  `Precio_Venta` decimal(10,2) NOT NULL COMMENT 'Precio de venta del articulo',
  `Precio_Renta` decimal(10,2) NOT NULL COMMENT 'Precio de renta por dia',
  `Stock` int(11) NOT NULL DEFAULT 0 COMMENT 'Cantidad total de trajes disponibles con este codigo o ID',
  `Disponible` int(11) NOT NULL DEFAULT 0 COMMENT 'Cantidad Disponible actual',
  `Estado` enum('Activo','Inactivo') DEFAULT 'Activo' COMMENT 'Estado del producto'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `inventario`
--

INSERT INTO `inventario` (`Codigo_Barras`, `Descripcion`, `Talla`, `Color`, `Categoria`, `Precio_Venta`, `Precio_Renta`, `Stock`, `Disponible`, `Estado`) VALUES
('diseny0008', 'ejemplo', 'M', 'negro', 'Superheroes', 15500.00, 125.00, 10, 5, 'Activo'),
('DISNEY0000', 'SPIDERMAN CLASICO', 'L', 'ROJO', 'Superheroes', 2000.00, 300.00, 10, 0, 'Activo'),
('DISNEY0001', 'TRAJE SUPER-MAN', 'XS', 'AZUL', 'Superheroes', 1500.00, 350.00, 10, 8, 'Activo'),
('DISNEY0003', 'TRAJE WOODY', 'S', 'CAFE', 'Fantasia', 1850.00, 250.00, 10, 8, 'Activo'),
('DISNEY0004', 'TRAJE BETTY BOOP', 'L', 'ROSA', 'Fantasia', 2500.00, 380.00, 15, 8, 'Activo'),
('DISNEY001', 'Traje buzz lightyear', 'XS', 'blanco', 'Superheroes', 1200.00, 350.00, 2, 2, 'Inactivo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `parametros_sistema`
--

CREATE TABLE `parametros_sistema` (
  `Parametro` varchar(255) NOT NULL,
  `Valor` text NOT NULL,
  `Descripcion` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `parametros_sistema`
--

INSERT INTO `parametros_sistema` (`Parametro`, `Valor`, `Descripcion`) VALUES
('Alerta_Stock_Minimo', '5', 'Valor por defecto para alerta de stock bajo'),
('Descuento_Volumen_Cantidad', '3', 'Cantidad m?nima de ?tems para aplicar descuento por volumen'),
('Descuento_Volumen_Porcentaje', '10.0', 'Porcentaje de descuento por volumen'),
('Dias_Gracia_Renta', '2', 'N?mero de d?as extra antes de que una renta se considere vencida'),
('Direccion_Negocio', 'Prueba de calle 123', 'Direcci?n del negocio'),
('Formato_Recibo', 'Nombre_Negocio,Direccion_Negocio,Telefono_Negocio,Cliente,Disfraces,Total,Dia_Renta,Dia_Devolucion', 'Campos a incluir en el recibo, separados por comas'),
('Limite_Disfraces_Renta', '10', 'N?mero m?ximo de disfraces que un cliente puede rentar simult?neamente'),
('Metodos_Pago', 'Efectivo,Tarjeta,Transferencia', 'Lista de m?todos de pago aceptados, separados por comas'),
('Nombre_Negocio', 'CARE', 'Nombre del negocio que aparece en reportes y recibos'),
('Penalizacion_Vencimiento', '50.00', 'Monto fijo de penalizaci?n por renta vencida (en pesos)'),
('Requerir_Deposito', '0', '1 para S? requerir dep?sito, 0 para NO requerirlo'),
('Telefono_Negocio', '618-123-4567', 'Tel?fono de contacto del negocio');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `rentas`
--

CREATE TABLE `rentas` (
  `Id_Renta` int(11) NOT NULL COMMENT 'PK, identificador de la renta',
  `Id_Cliente` int(11) NOT NULL COMMENT 'Referencia a la tabla de clientes',
  `Id_Usuario` int(11) NOT NULL COMMENT 'Empleado que registro la renta',
  `Fecha_Renta` datetime DEFAULT current_timestamp() COMMENT 'Fecha inicio de renta',
  `Fecha_Devolucion` datetime NOT NULL COMMENT 'fecha que deberia regresar el disfraz',
  `Fecha_Devuelto` datetime DEFAULT NULL,
  `Penalizacion` decimal(10,2) DEFAULT 0.00 COMMENT 'Penalizacion a pagar por fecha de retraso',
  `Dias_Renta` int(11) NOT NULL COMMENT 'Dias posteriores de la fecha_devolucion',
  `Total` decimal(10,2) NOT NULL COMMENT 'Total a pagar',
  `Deposito` decimal(10,2) DEFAULT 0.00 COMMENT 'Deposito en garantia',
  `Estado` enum('Activa','Devuelto','Vencida') DEFAULT 'Activa' COMMENT 'Estado de la renta'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `rentas`
--

INSERT INTO `rentas` (`Id_Renta`, `Id_Cliente`, `Id_Usuario`, `Fecha_Renta`, `Fecha_Devolucion`, `Fecha_Devuelto`, `Penalizacion`, `Dias_Renta`, `Total`, `Deposito`, `Estado`) VALUES
(22, 25, 28, '2025-11-29 14:49:45', '2025-12-01 14:49:45', '2025-11-29 15:12:31', 0.00, 2, 600.00, 2000.00, 'Devuelto'),
(46, 31, 31, '2025-12-02 08:44:52', '2025-12-04 08:44:52', '2025-12-02 08:56:27', 0.00, 2, 600.00, 2000.00, 'Devuelto'),
(47, 25, 31, '2025-12-02 08:46:38', '2025-12-06 08:46:38', NULL, 0.00, 4, 1200.00, 2000.00, 'Activa'),
(48, 31, 31, '2025-12-02 08:51:15', '2025-12-07 08:51:15', NULL, 0.00, 5, 1500.00, 2000.00, 'Activa'),
(49, 25, 31, '2025-12-02 08:56:08', '2025-12-04 08:56:08', NULL, 0.00, 2, 600.00, 2000.00, 'Activa'),
(50, 31, 31, '2025-12-02 09:00:01', '2025-12-07 09:00:01', NULL, 0.00, 5, 1500.00, 2000.00, 'Activa'),
(51, 25, 31, '2025-12-02 15:38:49', '2025-12-04 15:38:49', NULL, 0.00, 2, 600.00, 2000.00, 'Activa'),
(52, 31, 31, '2025-12-02 16:00:40', '2025-12-05 16:00:40', NULL, 0.00, 3, 900.00, 0.00, 'Activa'),
(53, 31, 31, '2025-12-02 16:49:07', '2025-12-12 16:49:07', NULL, 0.00, 10, 2500.00, 0.00, 'Activa'),
(54, 25, 31, '2025-12-02 17:07:24', '2025-12-12 17:07:24', NULL, 0.00, 10, 2500.00, 0.00, 'Activa'),
(55, 25, 31, '2025-12-02 17:17:13', '2025-12-03 17:17:13', NULL, 0.00, 1, 380.00, 0.00, 'Activa'),
(56, 31, 31, '2025-12-02 17:36:31', '2025-12-05 17:36:31', NULL, 0.00, 3, 900.00, 0.00, 'Activa'),
(57, 25, 31, '2025-12-02 17:59:15', '2025-12-04 17:59:15', NULL, 0.00, 2, 600.00, 0.00, 'Activa'),
(58, 25, 49, '2025-12-02 18:45:16', '2026-01-21 18:45:16', NULL, 0.00, 50, 30000.00, 0.00, 'Activa'),
(59, 25, 49, '2025-12-02 18:59:02', '2026-02-20 18:59:02', NULL, 0.00, 80, 24000.00, 0.00, 'Activa'),
(60, 25, 31, '2025-12-03 11:35:06', '2025-12-08 11:35:06', NULL, 0.00, 5, 625.00, 0.00, 'Activa'),
(61, 31, 31, '2025-12-03 13:46:22', '2026-03-13 13:46:22', NULL, 0.00, 100, 128000.00, 0.00, 'Activa'),
(62, 31, 31, '2025-12-03 14:08:56', '2025-12-08 14:08:56', NULL, 0.00, 5, 625.00, 0.00, 'Activa'),
(63, 31, 31, '2025-12-04 17:25:55', '2025-12-09 17:25:55', NULL, 0.00, 5, 1900.00, 0.00, 'Activa'),
(64, 31, 31, '2025-12-04 17:27:49', '2025-12-07 17:27:49', NULL, 0.00, 3, 1800.00, 0.00, 'Activa'),
(65, 31, 31, '2025-12-04 17:28:36', '2025-12-06 17:28:36', NULL, 0.00, 2, 1010.00, 0.00, 'Activa'),
(66, 31, 31, '2025-12-04 17:46:48', '2025-12-07 17:46:48', NULL, 0.00, 3, 375.00, 0.00, 'Activa'),
(67, 31, 31, '2025-12-04 18:07:14', '2025-12-05 18:07:14', '2025-12-05 17:37:11', 0.00, 1, 125.00, 0.00, 'Devuelto'),
(68, 31, 31, '2025-12-04 18:24:40', '2025-12-14 18:24:40', '2025-12-05 17:34:07', 0.00, 10, 3000.00, 0.00, 'Devuelto'),
(69, 31, 31, '2025-12-05 17:31:11', '2026-01-24 17:31:11', '2025-12-05 17:34:04', 0.00, 50, 12500.00, 0.00, 'Devuelto');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `Id_usuario` int(11) NOT NULL COMMENT 'PK, Identificador unico',
  `Usuario` varchar(255) NOT NULL COMMENT 'nombre de usuario',
  `Nombre` text NOT NULL COMMENT 'nombre',
  `Apellido_Paterno` text NOT NULL COMMENT 'Apellido paterno',
  `Password` varchar(255) NOT NULL COMMENT 'contrasena',
  `Pregunta_Seguridad` varchar(255) DEFAULT NULL,
  `Respuesta_Seguridad` varchar(255) DEFAULT NULL,
  `Rol` enum('empleado','admin') DEFAULT 'empleado' COMMENT 'rol asignado',
  `Fecha_Registro` datetime DEFAULT current_timestamp() COMMENT 'fecha de creacion'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`Id_usuario`, `Usuario`, `Nombre`, `Apellido_Paterno`, `Password`, `Pregunta_Seguridad`, `Respuesta_Seguridad`, `Rol`, `Fecha_Registro`) VALUES
(28, 'admin', 'Administrador', 'Sistema', 'admin123', NULL, NULL, 'empleado', '2025-11-22 11:08:31'),
(31, 'Rena', 'Renatha', 'Becerril', 'admin123', NULL, NULL, 'admin', '2025-11-24 07:47:38'),
(49, 'ByteOrtega', 'Jorge', 'Paredes', '1234567890', '¿Ciudad donde naciste?', 'Yucatan', 'admin', '2025-12-02 18:24:57'),
(52, 'JorgeParedes', 'Jorge', 'Paredes', 'admin123', '¿Comida favorita?', 'Tamales', 'empleado', '2025-12-11 20:12:04');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `ventas`
--

CREATE TABLE `ventas` (
  `Id_Venta` int(11) NOT NULL COMMENT 'PK, Identificador del ticket de venta',
  `Folio` varchar(20) DEFAULT NULL COMMENT 'Folio ?nico autogenerado (ej: VEN-20250121-0001)',
  `Id_cliente` int(11) NOT NULL COMMENT 'referencia de cliente',
  `Usuario_id` int(11) NOT NULL COMMENT 'referencia de empleados, quien hace la venta',
  `fecha_venta` datetime DEFAULT current_timestamp() COMMENT 'Fecha de la venta',
  `Total` decimal(10,2) NOT NULL COMMENT 'total de la venta',
  `Descuento_Porcentaje` decimal(5,2) DEFAULT NULL COMMENT 'Porcentaje de descuento aplicado (0-100)',
  `Descuento_Monto` decimal(10,2) DEFAULT NULL COMMENT 'Monto en pesos del descuento',
  `Motivo_Descuento` text DEFAULT NULL COMMENT 'Justificaci?n del descuento',
  `Motivo_Venta` varchar(100) DEFAULT NULL COMMENT 'Evento especial (Halloween, Navidad, etc.)',
  `Notas` text DEFAULT NULL COMMENT 'Observaciones adicionales',
  `Estado` enum('Activa','Cancelada') DEFAULT NULL COMMENT 'Estado de la venta',
  `Cancelada_Por` int(11) DEFAULT NULL COMMENT 'ID del admin que cancel?',
  `Fecha_Cancelacion` datetime DEFAULT NULL COMMENT 'Fecha de cancelaci?n',
  `Motivo_Cancelacion` text DEFAULT NULL COMMENT 'Raz?n de la cancelaci?n',
  `metodo_pago` enum('Efectivo','tarjeta','Transferencia') DEFAULT 'Efectivo' COMMENT 'Forma de pago realizada'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `ventas`
--

INSERT INTO `ventas` (`Id_Venta`, `Folio`, `Id_cliente`, `Usuario_id`, `fecha_venta`, `Total`, `Descuento_Porcentaje`, `Descuento_Monto`, `Motivo_Descuento`, `Motivo_Venta`, `Notas`, `Estado`, `Cancelada_Por`, `Fecha_Cancelacion`, `Motivo_Cancelacion`, `metodo_pago`) VALUES
(17, 'VEN-173131-403c', 31, 31, '2025-12-11 17:31:31', 1850.00, 0.00, 0.00, '', '', NULL, 'Activa', NULL, NULL, NULL, 'Efectivo'),
(18, '20251211-00001', 31, 31, '2025-12-11 18:26:58', 17500.00, 0.00, 0.00, '', '', NULL, 'Activa', NULL, NULL, NULL, 'Efectivo'),
(19, '20251211-00002', 31, 31, '2025-12-11 18:27:16', 4000.00, 0.00, 0.00, '', '', NULL, 'Activa', NULL, NULL, NULL, 'Efectivo'),
(20, '20251211-00003', 44, 52, '2025-12-11 20:14:30', 7500.00, 0.00, 0.00, '', '', NULL, 'Activa', NULL, NULL, NULL, 'tarjeta');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `clientes`
--
ALTER TABLE `clientes`
  ADD PRIMARY KEY (`Id_cliente`),
  ADD KEY `idx_telefono` (`Telefono`);

--
-- Indices de la tabla `configuracion`
--
ALTER TABLE `configuracion`
  ADD PRIMARY KEY (`Id_Config`),
  ADD UNIQUE KEY `Nombre_Config` (`Nombre_Config`);

--
-- Indices de la tabla `detalle_rentas`
--
ALTER TABLE `detalle_rentas`
  ADD PRIMARY KEY (`Id_DetalleRenta`),
  ADD KEY `Codigo_Barras` (`Codigo_Barras`),
  ADD KEY `idx_renta` (`Id_Renta`);

--
-- Indices de la tabla `detalle_ventas`
--
ALTER TABLE `detalle_ventas`
  ADD PRIMARY KEY (`ID_DetalleVenta`),
  ADD KEY `Codigo_Barras` (`Codigo_Barras`),
  ADD KEY `idx_venta` (`Id_Venta`);

--
-- Indices de la tabla `inventario`
--
ALTER TABLE `inventario`
  ADD PRIMARY KEY (`Codigo_Barras`),
  ADD KEY `idx_categoria` (`Categoria`(768)),
  ADD KEY `idx_estado` (`Estado`);

--
-- Indices de la tabla `parametros_sistema`
--
ALTER TABLE `parametros_sistema`
  ADD PRIMARY KEY (`Parametro`);

--
-- Indices de la tabla `rentas`
--
ALTER TABLE `rentas`
  ADD PRIMARY KEY (`Id_Renta`),
  ADD KEY `Id_Cliente` (`Id_Cliente`),
  ADD KEY `Id_Usuario` (`Id_Usuario`),
  ADD KEY `idx_estado` (`Estado`),
  ADD KEY `idx_fecha_devolucion` (`Fecha_Devolucion`),
  ADD KEY `idx_estado_fecha` (`Estado`,`Fecha_Devolucion`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`Id_usuario`),
  ADD UNIQUE KEY `Usuario` (`Usuario`),
  ADD KEY `idx_usuario` (`Usuario`);

--
-- Indices de la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD PRIMARY KEY (`Id_Venta`),
  ADD UNIQUE KEY `Folio` (`Folio`),
  ADD KEY `Usuario_id` (`Usuario_id`),
  ADD KEY `idx_fecha_venta` (`fecha_venta`),
  ADD KEY `idx_cliente` (`Id_cliente`),
  ADD KEY `fk_ventas_cancelada_por` (`Cancelada_Por`),
  ADD KEY `idx_folio` (`Folio`),
  ADD KEY `idx_estado` (`Estado`),
  ADD KEY `idx_motivo_venta` (`Motivo_Venta`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `clientes`
--
ALTER TABLE `clientes`
  MODIFY `Id_cliente` int(11) NOT NULL AUTO_INCREMENT COMMENT 'PK, Identificador unico', AUTO_INCREMENT=45;

--
-- AUTO_INCREMENT de la tabla `configuracion`
--
ALTER TABLE `configuracion`
  MODIFY `Id_Config` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT de la tabla `detalle_rentas`
--
ALTER TABLE `detalle_rentas`
  MODIFY `Id_DetalleRenta` int(11) NOT NULL AUTO_INCREMENT COMMENT 'PK', AUTO_INCREMENT=77;

--
-- AUTO_INCREMENT de la tabla `detalle_ventas`
--
ALTER TABLE `detalle_ventas`
  MODIFY `ID_DetalleVenta` int(11) NOT NULL AUTO_INCREMENT COMMENT 'PK', AUTO_INCREMENT=23;

--
-- AUTO_INCREMENT de la tabla `rentas`
--
ALTER TABLE `rentas`
  MODIFY `Id_Renta` int(11) NOT NULL AUTO_INCREMENT COMMENT 'PK, identificador de la renta', AUTO_INCREMENT=70;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `Id_usuario` int(11) NOT NULL AUTO_INCREMENT COMMENT 'PK, Identificador unico', AUTO_INCREMENT=53;

--
-- AUTO_INCREMENT de la tabla `ventas`
--
ALTER TABLE `ventas`
  MODIFY `Id_Venta` int(11) NOT NULL AUTO_INCREMENT COMMENT 'PK, Identificador del ticket de venta', AUTO_INCREMENT=21;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `detalle_rentas`
--
ALTER TABLE `detalle_rentas`
  ADD CONSTRAINT `detalle_rentas_ibfk_1` FOREIGN KEY (`Id_Renta`) REFERENCES `rentas` (`Id_Renta`) ON DELETE CASCADE,
  ADD CONSTRAINT `detalle_rentas_ibfk_2` FOREIGN KEY (`Codigo_Barras`) REFERENCES `inventario` (`Codigo_Barras`);

--
-- Filtros para la tabla `detalle_ventas`
--
ALTER TABLE `detalle_ventas`
  ADD CONSTRAINT `detalle_ventas_ibfk_1` FOREIGN KEY (`Id_Venta`) REFERENCES `ventas` (`Id_Venta`) ON DELETE CASCADE,
  ADD CONSTRAINT `detalle_ventas_ibfk_2` FOREIGN KEY (`Codigo_Barras`) REFERENCES `inventario` (`Codigo_Barras`);

--
-- Filtros para la tabla `rentas`
--
ALTER TABLE `rentas`
  ADD CONSTRAINT `rentas_ibfk_1` FOREIGN KEY (`Id_Cliente`) REFERENCES `clientes` (`Id_cliente`),
  ADD CONSTRAINT `rentas_ibfk_2` FOREIGN KEY (`Id_Usuario`) REFERENCES `usuarios` (`Id_usuario`);

--
-- Filtros para la tabla `ventas`
--
ALTER TABLE `ventas`
  ADD CONSTRAINT `fk_ventas_cancelada_por` FOREIGN KEY (`Cancelada_Por`) REFERENCES `usuarios` (`Id_usuario`),
  ADD CONSTRAINT `ventas_ibfk_1` FOREIGN KEY (`Id_cliente`) REFERENCES `clientes` (`Id_cliente`),
  ADD CONSTRAINT `ventas_ibfk_2` FOREIGN KEY (`Usuario_id`) REFERENCES `usuarios` (`Id_usuario`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
