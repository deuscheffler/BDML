CREATE DATABASE BD_ML_RELACIONAL;
GO

-- Crear tabla CLIENTE
CREATE TABLE Cliente
(
    id_cliente INT IDENTITY(1,1) PRIMARY KEY,

    ciudad_cliente VARCHAR(100) NOT NULL,

    pais_cliente VARCHAR(100) NOT NULL,

    latitud DECIMAL(10,7) NULL,

    longitud DECIMAL(10,7) NULL
);
GO
-- Crear tabla CATEGORIA
CREATE TABLE Categoria
(
    id_categoria INT IDENTITY(1,1) PRIMARY KEY,

    nombre_categoria VARCHAR(100) NOT NULL UNIQUE
);
GO
--Crear tabla PRODUCTO
CREATE TABLE Producto
(
    id_producto INT IDENTITY(1,1) PRIMARY KEY,

    nombre_producto VARCHAR(200) NOT NULL,

    precio_producto DECIMAL(10,2),

    precio_base DECIMAL(10,2),

    id_categoria INT NOT NULL
);
GO
--Crear tabla DESTINO
CREATE TABLE Destino
(
    id_destino INT IDENTITY(1,1) PRIMARY KEY,

    ciudad_destino VARCHAR(100),

    estado_destino VARCHAR(100),

    pais_destino VARCHAR(100),

    region_destino VARCHAR(100)
);
GO
--Crear tabla ENVIO
CREATE TABLE Envio
(
    id_envio INT IDENTITY(1,1) PRIMARY KEY,

    fecha_envio DATETIME NOT NULL,

    modo_envio VARCHAR(50),

    estado_entrega VARCHAR(100),

    dias_envio_real INT,

    dias_envio_prog INT
);
GO
--Crear tabla PEDIDO



CREATE TABLE Pedido
(
    id_pedido INT IDENTITY(1,1) PRIMARY KEY,

    fecha_pedido DATETIME NOT NULL,

    tipo_transaccion VARCHAR(50),

    estado_pedido VARCHAR(50) NOT NULL,

    beneficio_pedido DECIMAL(12,2),

    ventas_cliente DECIMAL(12,2),

    margen_ganancia_item DECIMAL(12,4),

    cantidad INT,

    ventas DECIMAL(12,2),

    total_item DECIMAL(12,2),

    ganancia_pedido DECIMAL(12,2),

    riesgo_retraso BIT,

    id_cliente INT NOT NULL,

    id_producto INT NOT NULL,

    id_destino INT NOT NULL,

    id_envio INT NOT NULL
);
GO



SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES;

USE BD_ML_RELACIONAL;
GO

DROP TABLE IF EXISTS Pedido;
DROP TABLE IF EXISTS Envio;
DROP TABLE IF EXISTS Destino;
DROP TABLE IF EXISTS Producto;
DROP TABLE IF EXISTS Categoria;
DROP TABLE IF EXISTS Cliente;
GO

CREATE TABLE UbicacionCliente
(
    id_ubicacion_cliente INT IDENTITY(1,1) PRIMARY KEY,

    ciudad_cliente VARCHAR(100) NOT NULL,

    pais_cliente VARCHAR(100) NOT NULL,

    latitud DECIMAL(10,7),

    longitud DECIMAL(10,7)
);
GO
CREATE TABLE Categoria
(
    id_categoria INT IDENTITY(1,1) PRIMARY KEY,

    nombre_categoria VARCHAR(100) NOT NULL UNIQUE
);
GO

CREATE TABLE Producto
(
    id_producto INT IDENTITY(1,1) PRIMARY KEY,

    nombre_producto VARCHAR(200) NOT NULL,

    precio_producto DECIMAL(10,2),

    precio_base DECIMAL(10,2),

    id_categoria INT NOT NULL
);
GO

CREATE TABLE Destino
(
    id_destino INT IDENTITY(1,1) PRIMARY KEY,

    ciudad_destino VARCHAR(100),

    estado_destino VARCHAR(100),

    pais_destino VARCHAR(100),

    region_destino VARCHAR(100)
);
GO

CREATE TABLE Pedido
(
    id_pedido INT IDENTITY(1,1) PRIMARY KEY,

    fecha_pedido DATETIME NOT NULL,

    fecha_envio DATETIME NOT NULL,

    tipo_transaccion VARCHAR(50),

    estado_pedido VARCHAR(50),

    estado_entrega VARCHAR(100),

    modo_envio VARCHAR(50),

    dias_envio_real INT,

    dias_envio_prog INT,

    beneficio_pedido DECIMAL(12,2),

    ventas_cliente DECIMAL(12,2),

    margen_ganancia_item DECIMAL(12,4),

    cantidad INT,

    ventas DECIMAL(12,2),

    total_item DECIMAL(12,2),

    ganancia_pedido DECIMAL(12,2),

    riesgo_retraso BIT,

    id_producto INT NOT NULL,

    id_destino INT NOT NULL,

    id_ubicacion_cliente INT NOT NULL
);
GO

-- Agregar restricciones UNIQUE
ALTER TABLE UbicacionCliente
ADD CONSTRAINT UQ_UbicacionCliente
UNIQUE
(
    ciudad_cliente,
    pais_cliente,
    latitud,
    longitud
);
GO

ALTER TABLE Categoria
ADD CONSTRAINT UQ_Categoria
UNIQUE(nombre_categoria);
GO


ALTER TABLE Producto
ADD CONSTRAINT UQ_Producto
UNIQUE
(
    nombre_producto,
    id_categoria
);
GO

ALTER TABLE Destino
ADD CONSTRAINT UQ_Destino
UNIQUE
(
    ciudad_destino,
    estado_destino,
    pais_destino,
    region_destino
);
GO

-- proceso ETL usará Pero si accidentalmente se ejecuta dos veces, SQL Server impedirá insertar registros duplicados.



-- Crear índices

CREATE INDEX IX_Producto_Categoria
ON Producto(id_categoria);
GO

CREATE INDEX IX_Pedido_Producto
ON Pedido(id_producto);
GO

CREATE INDEX IX_Pedido_Destino
ON Pedido(id_destino);
GO

CREATE INDEX IX_Pedido_Ubicacion
ON Pedido(id_ubicacion_cliente);
GO