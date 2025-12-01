-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 25-11-2025 a las 00:19:11
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
  `Fecha_Registro` datetime DEFAULT current_timestamp() COMMENT 'Fecha de creacion'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
(1, 'PENALIZACION_DIA', '50.00', 'Monto de penalizaci?n por d?a de retraso en rentas', '2025-11-21 22:12:34');

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
('DISNEY0000', 'SPIDERMAN CLASICO', 'L', 'ROJO', 'Superheroes', 2000.00, 300.00, 5, 0, 'Activo'),
('DISNEY001', 'Traje buzz lightyear', 'XS', 'blanco', 'Superheroes', 1200.00, 350.00, 2, 2, 'Inactivo');

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
  `Rol` enum('empleado','admin') DEFAULT 'empleado' COMMENT 'rol asignado',
  `Fecha_Registro` datetime DEFAULT current_timestamp() COMMENT 'fecha de creacion'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`Id_usuario`, `Usuario`, `Nombre`, `Apellido_Paterno`, `Password`, `Rol`, `Fecha_Registro`) VALUES
(28, 'admin', 'Administrador', 'Sistema', 'admin123', 'empleado', '2025-11-22 11:08:31'),
(31, 'Rena', 'Renatha', 'Becerril', 'admin123', 'admin', '2025-11-24 07:47:38');

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
  MODIFY `Id_cliente` int(11) NOT NULL AUTO_INCREMENT COMMENT 'PK, Identificador unico', AUTO_INCREMENT=25;

--
-- AUTO_INCREMENT de la tabla `configuracion`
--
ALTER TABLE `configuracion`
  MODIFY `Id_Config` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT de la tabla `detalle_rentas`
--
ALTER TABLE `detalle_rentas`
  MODIFY `Id_DetalleRenta` int(11) NOT NULL AUTO_INCREMENT COMMENT 'PK', AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT de la tabla `detalle_ventas`
--
ALTER TABLE `detalle_ventas`
  MODIFY `ID_DetalleVenta` int(11) NOT NULL AUTO_INCREMENT COMMENT 'PK', AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT de la tabla `rentas`
--
ALTER TABLE `rentas`
  MODIFY `Id_Renta` int(11) NOT NULL AUTO_INCREMENT COMMENT 'PK, identificador de la renta', AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `Id_usuario` int(11) NOT NULL AUTO_INCREMENT COMMENT 'PK, Identificador unico', AUTO_INCREMENT=32;

--
-- AUTO_INCREMENT de la tabla `ventas`
--
ALTER TABLE `ventas`
  MODIFY `Id_Venta` int(11) NOT NULL AUTO_INCREMENT COMMENT 'PK, Identificador del ticket de venta', AUTO_INCREMENT=15;

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
