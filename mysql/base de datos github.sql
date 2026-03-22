-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         12.1.2-MariaDB - MariaDB Server
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.11.0.7065
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para consultorio_medico
CREATE DATABASE IF NOT EXISTS `consultorio_medico` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `consultorio_medico`;

-- Volcando estructura para tabla consultorio_medico.atencion_medica
CREATE TABLE IF NOT EXISTS `atencion_medica` (
  `id_atencion` int(11) NOT NULL,
  `diagnosticos` text DEFAULT NULL,
  `observaciones` text DEFAULT NULL,
  `fecha_atencion` date DEFAULT NULL,
  `id_cita` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_atencion`),
  KEY `id_cita` (`id_cita`),
  CONSTRAINT `atencion_medica_ibfk_1` FOREIGN KEY (`id_cita`) REFERENCES `cita` (`id_cita`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla consultorio_medico.atencion_medica: ~6 rows (aproximadamente)
INSERT INTO `atencion_medica` (`id_atencion`, `diagnosticos`, `observaciones`, `fecha_atencion`, `id_cita`) VALUES
	(1, 'Gripe común', 'Reposo 3 días', '2026-02-25', 1),
	(2, 'Sano', 'Sin novedad', '2026-02-26', 2),
	(3, 'Gastritis', 'Dieta blanda', '2026-02-27', 3),
	(4, 'Cefalea', 'Evitar luces fuertes', '2026-02-28', 4),
	(5, 'Rinitis', 'Antihistamínicos', '2026-03-01', 5),
	(6, 'Sano', 'Paciente estable', '2026-03-01', 6);

-- Volcando estructura para tabla consultorio_medico.cita
CREATE TABLE IF NOT EXISTS `cita` (
  `id_cita` int(11) NOT NULL,
  `fecha` date DEFAULT NULL,
  `hora` time DEFAULT NULL,
  `motivo_consulta` varchar(255) DEFAULT NULL,
  `estado` varchar(50) DEFAULT NULL,
  `id_paciente` int(11) DEFAULT NULL,
  `id_empleado` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_cita`),
  KEY `id_paciente` (`id_paciente`),
  KEY `id_empleado` (`id_empleado`),
  CONSTRAINT `cita_ibfk_1` FOREIGN KEY (`id_paciente`) REFERENCES `paciente` (`id_paciente`),
  CONSTRAINT `cita_ibfk_2` FOREIGN KEY (`id_empleado`) REFERENCES `empleado` (`id_empleado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla consultorio_medico.cita: ~6 rows (aproximadamente)
INSERT INTO `cita` (`id_cita`, `fecha`, `hora`, `motivo_consulta`, `estado`, `id_paciente`, `id_empleado`) VALUES
	(1, '2026-02-25', '08:00:00', 'Gripe', 'Atendida', 1, 1),
	(2, '2026-02-26', '09:00:00', 'Control', 'Atendida', 2, 6),
	(3, '2026-02-27', '10:00:00', 'Dolor estomacal', 'Atendida', 3, 1),
	(4, '2026-02-28', '11:00:00', 'Migraña', 'Atendida', 4, 7),
	(5, '2026-03-01', '08:30:00', 'Alergia', 'Atendida', 5, 1),
	(6, '2026-03-01', '09:30:00', 'Chequeo', 'Atendida', 6, 6);

-- Volcando estructura para tabla consultorio_medico.compra
CREATE TABLE IF NOT EXISTS `compra` (
  `id_compra` int(11) NOT NULL,
  `fecha` date DEFAULT NULL,
  `total` decimal(10,2) DEFAULT NULL,
  `id_proveedor` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_compra`),
  KEY `id_proveedor` (`id_proveedor`),
  CONSTRAINT `compra_ibfk_1` FOREIGN KEY (`id_proveedor`) REFERENCES `proveedor` (`id_proveedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla consultorio_medico.compra: ~0 rows (aproximadamente)

-- Volcando estructura para tabla consultorio_medico.detalle_compra
CREATE TABLE IF NOT EXISTS `detalle_compra` (
  `id_detalle_compra` int(11) NOT NULL,
  `cantidad` int(11) DEFAULT NULL,
  `costo_unitario` decimal(10,2) DEFAULT NULL,
  `id_compra` int(11) DEFAULT NULL,
  `id_medicamento` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_detalle_compra`),
  KEY `id_compra` (`id_compra`),
  KEY `id_medicamento` (`id_medicamento`),
  CONSTRAINT `detalle_compra_ibfk_1` FOREIGN KEY (`id_compra`) REFERENCES `compra` (`id_compra`),
  CONSTRAINT `detalle_compra_ibfk_2` FOREIGN KEY (`id_medicamento`) REFERENCES `medicamento` (`id_medicamento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla consultorio_medico.detalle_compra: ~0 rows (aproximadamente)

-- Volcando estructura para tabla consultorio_medico.detalle_venta
CREATE TABLE IF NOT EXISTS `detalle_venta` (
  `id_detalle_venta` int(11) NOT NULL,
  `cantidad` int(11) DEFAULT NULL,
  `subtotal` decimal(10,2) DEFAULT NULL,
  `id_venta` int(11) DEFAULT NULL,
  `id_medicamento` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_detalle_venta`),
  KEY `id_venta` (`id_venta`),
  KEY `id_medicamento` (`id_medicamento`),
  CONSTRAINT `detalle_venta_ibfk_1` FOREIGN KEY (`id_venta`) REFERENCES `venta` (`id_venta`),
  CONSTRAINT `detalle_venta_ibfk_2` FOREIGN KEY (`id_medicamento`) REFERENCES `medicamento` (`id_medicamento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla consultorio_medico.detalle_venta: ~0 rows (aproximadamente)

-- Volcando estructura para tabla consultorio_medico.empleado
CREATE TABLE IF NOT EXISTS `empleado` (
  `id_empleado` int(11) NOT NULL,
  `nombres` varchar(255) DEFAULT NULL,
  `apellidos` varchar(255) DEFAULT NULL,
  `cargo` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `correo` varchar(255) DEFAULT NULL,
  `fecha_ingreso` date DEFAULT NULL,
  PRIMARY KEY (`id_empleado`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla consultorio_medico.empleado: ~12 rows (aproximadamente)
INSERT INTO `empleado` (`id_empleado`, `nombres`, `apellidos`, `cargo`, `telefono`, `correo`, `fecha_ingreso`) VALUES
	(1, 'Andrés Felipe', 'Salazar Ruiz', 'Médico General', '0984123456', 'andres.salazar.m@gmail.com', '2023-05-12'),
	(2, 'Beatriz Elena', 'Morocho Paz', 'Enfermera', '0995678901', 'b.morocho.paz@gmail.com', '2023-08-20'),
	(3, 'Christian Paul', 'Vaca Torres', 'Administrativo', '0971122334', 'chris.vaca.t@gmail.com', '2024-01-10'),
	(4, 'Diana Marcela', 'Gómez Jaramillo', 'Recepcionista', '0963344556', 'diana.gomez.j@gmail.com', '2024-02-15'),
	(5, 'Esteban Josué', 'Paredes León', 'Especialista', '0959988776', 'esteban.paredes.l@gmail.com', '2024-02-21'),
	(6, 'Ricardo Javier', 'Mendoza Castro', 'Médico General', '0991234567', 'r.mendoza@gmail.com', '2024-05-15'),
	(7, 'Valeria Sofía', 'Ortiz Ramos', 'Médico General', '0987654321', 'v.ortiz.med@gmail.com', '2024-06-01'),
	(8, 'Fernando David', 'López Villalba', 'Enfermero', '0978899001', 'f.lopez.enf@gmail.com', '2024-08-12'),
	(9, 'Mónica Patricia', 'Suárez Holguín', 'Enfermera', '0965544332', 'monica.suarez@gmail.com', '2025-01-10'),
	(10, 'Santiago Israel', 'Guerrero Pozo', 'Enfermero', '0952233445', 's.guerrero.p@gmail.com', '2025-02-20');

-- Volcando estructura para tabla consultorio_medico.medicamento
CREATE TABLE IF NOT EXISTS `medicamento` (
  `id_medicamento` int(11) NOT NULL,
  `nombre` varchar(255) DEFAULT NULL,
  `categoria` varchar(100) DEFAULT NULL,
  `precio` decimal(10,2) DEFAULT NULL,
  `stock` int(11) DEFAULT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  PRIMARY KEY (`id_medicamento`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla consultorio_medico.medicamento: ~0 rows (aproximadamente)

-- Volcando estructura para tabla consultorio_medico.paciente
CREATE TABLE IF NOT EXISTS `paciente` (
  `id_paciente` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_paciente`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla consultorio_medico.paciente: ~10 rows (aproximadamente)
INSERT INTO `paciente` (`id_paciente`, `nombre`) VALUES
	(1, 'Marlene Tipán'),
	(2, 'Leonel Montoya'),
	(3, 'Said Reyes'),
	(4, 'Esteban Paredes'),
	(5, 'Sebastian Bautista'),
	(6, 'Henry Salazar'),
	(7, 'Giselle Medina'),
	(8, 'Karina Soria'),
	(9, 'María Tipán'),
	(10, 'Sylvia Tipán');

-- Volcando estructura para tabla consultorio_medico.proveedor
CREATE TABLE IF NOT EXISTS `proveedor` (
  `id_proveedor` int(11) NOT NULL,
  `nombre` varchar(255) DEFAULT NULL,
  `tipo_producto` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_proveedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla consultorio_medico.proveedor: ~0 rows (aproximadamente)

-- Volcando estructura para tabla consultorio_medico.tratamiento
CREATE TABLE IF NOT EXISTS `tratamiento` (
  `id_tratamiento` int(11) NOT NULL,
  `tipo_tratamiento` varchar(255) DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  `id_atencion` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_tratamiento`),
  KEY `id_atencion` (`id_atencion`),
  CONSTRAINT `tratamiento_ibfk_1` FOREIGN KEY (`id_atencion`) REFERENCES `atencion_medica` (`id_atencion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla consultorio_medico.tratamiento: ~0 rows (aproximadamente)

-- Volcando estructura para tabla consultorio_medico.usuarios
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) DEFAULT NULL,
  `mail` varchar(100) DEFAULT NULL,
  `password` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla consultorio_medico.usuarios: ~1 rows (aproximadamente)
INSERT INTO `usuarios` (`id_usuario`, `nombre`, `mail`, `password`) VALUES
	(1, 'BYRON', 'byrondark36@gmail.com', '123456');

-- Volcando estructura para tabla consultorio_medico.venta
CREATE TABLE IF NOT EXISTS `venta` (
  `id_venta` int(11) NOT NULL,
  `fecha` date DEFAULT NULL,
  `total` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`id_venta`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla consultorio_medico.venta: ~0 rows (aproximadamente)

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
