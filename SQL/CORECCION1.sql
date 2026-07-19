USE BD_ML_RELACIONAL;
GO

SELECT *
INTO DataCoSupplyChain_RAW
FROM ML_DATABASE.dbo.DataCoSupplyChain_RAW;
GO

-- Cargar la tabla Categoria

SELECT COUNT(*) AS TotalRegistros
FROM DataCoSupplyChain_RAW;

INSERT INTO Categoria (nombre_categoria)

SELECT DISTINCT
       categoria
FROM DataCoSupplyChain_RAW
WHERE categoria IS NOT NULL
ORDER BY categoria;

SELECT *
FROM Categoria
ORDER BY nombre_categoria;


-- Cargar UbicacionCliente

INSERT INTO UbicacionCliente
(
    ciudad_cliente,
    pais_cliente,
    latitud,
    longitud
)

SELECT DISTINCT

       ciudad_cliente,

       pais_cliente,

       latitud,

       longitud

FROM DataCoSupplyChain_RAW;

-- CARGAR DESTINO

INSERT INTO Destino
(
    ciudad_destino,
    estado_destino,
    pais_destino,
    region_destino
)

SELECT DISTINCT

       ciudad_destino,

       estado_destino,

       pais_destino,

       region_destino

FROM DataCoSupplyChain_RAW;


SELECT
    ciudad_cliente,
    pais_cliente,
    COUNT(*) AS Registros
FROM DataCoSupplyChain_RAW
GROUP BY
    ciudad_cliente,
    pais_cliente
ORDER BY Registros DESC;

SELECT
    ciudad_cliente,
    pais_cliente,
    COUNT(DISTINCT latitud) AS Latitudes,
    COUNT(DISTINCT longitud) AS Longitudes
FROM DataCoSupplyChain_RAW
GROUP BY
    ciudad_cliente,
    pais_cliente
HAVING COUNT(DISTINCT latitud) > 1
    OR COUNT(DISTINCT longitud) > 1
ORDER BY Latitudes DESC;


-- CARGA DE PRODUCTO

INSERT INTO Producto
(
    nombre_producto,
    precio_producto,
    precio_base,
    id_categoria
)

SELECT DISTINCT

    R.nombre_producto,

    R.precio_producto,

    R.precio_base,

    C.id_categoria

FROM DataCoSupplyChain_RAW R

INNER JOIN Categoria C
ON R.categoria = C.nombre_categoria

ORDER BY
    R.nombre_producto;
GO

SELECT TOP 20 *
FROM Producto
ORDER BY nombre_producto;

SELECT *
FROM Producto
WHERE id_categoria IS NULL;

SELECT COUNT(*) FROM Categoria;
SELECT COUNT(*) FROM Producto;
SELECT COUNT(*) FROM Destino;
SELECT COUNT(*) FROM UbicacionCliente;

SELECT
    ciudad_cliente,
    pais_cliente,
    COUNT(*) AS Repetidos
FROM UbicacionCliente
GROUP BY
    ciudad_cliente,
    pais_cliente
HAVING COUNT(*) > 1;

TRUNCATE TABLE UbicacionCliente;

INSERT INTO UbicacionCliente
(
    ciudad_cliente,
    pais_cliente
)
SELECT DISTINCT
    ciudad_cliente,
    pais_cliente
FROM DataCoSupplyChain_RAW;

SELECT COUNT(*) AS Total
FROM UbicacionCliente;


-- crear vista de validacion

CREATE OR ALTER VIEW vw_ETL_Pedido
AS

SELECT

    R.*,

    P.id_producto,

    D.id_destino,

    U.id_ubicacion_cliente

FROM DataCoSupplyChain_RAW R

INNER JOIN Producto P
ON  R.nombre_producto = P.nombre_producto
AND R.precio_producto = P.precio_producto

INNER JOIN Destino D
ON R.ciudad_destino = D.ciudad_destino
AND R.estado_destino = D.estado_destino
AND R.pais_destino = D.pais_destino
AND R.region_destino = D.region_destino

INNER JOIN UbicacionCliente U
ON R.ciudad_cliente = U.ciudad_cliente
AND R.pais_cliente = U.pais_cliente;
GO

SELECT COUNT(*) AS Total
FROM vw_ETL_Pedido;

SELECT TOP 20 *

FROM vw_ETL_Pedido;

SELECT

COUNT(*) Total,

COUNT(id_producto) Productos,

COUNT(id_destino) Destinos,

COUNT(id_ubicacion_cliente) Clientes

FROM vw_ETL_Pedido;

SELECT COUNT(*) AS Productos_OK
FROM DataCoSupplyChain_RAW R
INNER JOIN Producto P
ON R.nombre_producto = P.nombre_producto
AND R.precio_producto = P.precio_producto;


SELECT COUNT(*) AS Destinos_OK
FROM DataCoSupplyChain_RAW R
INNER JOIN Destino D
ON R.ciudad_destino = D.ciudad_destino
AND R.estado_destino = D.estado_destino
AND R.pais_destino = D.pais_destino
AND R.region_destino = D.region_destino;

SELECT COUNT(*) AS Ubicaciones_OK
FROM DataCoSupplyChain_RAW R
INNER JOIN UbicacionCliente U
ON R.ciudad_cliente = U.ciudad_cliente
AND R.pais_cliente = U.pais_cliente;

SELECT
    nombre_producto,
    COUNT(DISTINCT precio_producto) AS PreciosProducto,
    COUNT(DISTINCT precio_base) AS PreciosBase
FROM DataCoSupplyChain_RAW
GROUP BY nombre_producto
HAVING COUNT(DISTINCT precio_producto) > 1
    OR COUNT(DISTINCT precio_base) > 1
ORDER BY nombre_producto;

SELECT
    COUNT(DISTINCT nombre_producto) AS Originales,
    COUNT(DISTINCT LTRIM(RTRIM(nombre_producto))) AS SinEspacios
FROM DataCoSupplyChain_RAW;

SELECT TOP 20

R.nombre_producto,

R.precio_producto AS Precio_RAW,

P.precio_producto AS Precio_TABLA

FROM DataCoSupplyChain_RAW R

LEFT JOIN Producto P

ON R.nombre_producto = P.nombre_producto

WHERE P.id_producto IS NULL;


DROP TABLE IF EXISTS Producto;
GO

CREATE TABLE Producto
(
    id_producto INT IDENTITY(1,1) PRIMARY KEY,

    nombre_producto VARCHAR(200) NOT NULL,

    id_categoria INT NOT NULL,

    CONSTRAINT UQ_Producto
        UNIQUE(nombre_producto)
);
GO

INSERT INTO Producto
(
    nombre_producto,
    id_categoria
)

SELECT DISTINCT

    R.nombre_producto,

    C.id_categoria

FROM DataCoSupplyChain_RAW R

INNER JOIN Categoria C
ON R.categoria = C.nombre_categoria

ORDER BY
    R.nombre_producto;
GO

SELECT COUNT(*) AS Productos
FROM Producto;


DROP TABLE IF EXISTS Pedido;
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

    precio_producto DECIMAL(12,2),
    precio_base DECIMAL(12,2),

    latitud DECIMAL(10,7),
    longitud DECIMAL(10,7),

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