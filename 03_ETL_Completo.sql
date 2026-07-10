INSERT INTO Pedido
(
    fecha_pedido,
    fecha_envio,

    tipo_transaccion,

    estado_pedido,

    estado_entrega,

    modo_envio,

    dias_envio_real,

    dias_envio_prog,

    precio_producto,

    precio_base,

    latitud,

    longitud,

    beneficio_pedido,

    ventas_cliente,

    margen_ganancia_item,

    cantidad,

    ventas,

    total_item,

    ganancia_pedido,

    riesgo_retraso,

    id_producto,

    id_destino,

    id_ubicacion_cliente
)

SELECT

    R.fecha_pedido,

    R.fecha_envio,

    R.tipo_transaccion,

    R.estado_pedido,

    R.estado_entrega,

    R.modo_envio,

    R.dias_envio_real,

    R.dias_envio_prog,

    R.precio_producto,

    R.precio_base,

    R.latitud,

    R.longitud,

    R.beneficio_pedido,

    R.ventas_cliente,

    R.margen_ganancia_item,

    R.cantidad,

    R.ventas,

    R.total_item,

    R.ganancia_pedido,

    R.riesgo_retraso,

    P.id_producto,

    D.id_destino,

    U.id_ubicacion_cliente

FROM DataCoSupplyChain_RAW R

INNER JOIN Producto P
ON R.nombre_producto = P.nombre_producto

INNER JOIN Destino D
ON R.ciudad_destino = D.ciudad_destino
AND R.estado_destino = D.estado_destino
AND R.pais_destino = D.pais_destino
AND R.region_destino = D.region_destino

INNER JOIN UbicacionCliente U
ON R.ciudad_cliente = U.ciudad_cliente
AND R.pais_cliente = U.pais_cliente;


SELECT COUNT(*) AS Pedidos
FROM Pedido;


DROP TABLE IF EXISTS Pedido;
GO

CREATE TABLE Pedido
(
    id_pedido INT IDENTITY(1,1) PRIMARY KEY,

    id_raw INT NOT NULL,

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

ALTER TABLE DataCoSupplyChain_RAW

ADD id_raw INT IDENTITY(1,1);


-- cargar los datos despues de la correccion

BEGIN TRY

BEGIN TRANSACTION;

INSERT INTO Pedido
(
    id_raw,
    fecha_pedido,
    fecha_envio,
    tipo_transaccion,
    estado_pedido,
    estado_entrega,
    modo_envio,
    dias_envio_real,
    dias_envio_prog,
    precio_producto,
    precio_base,
    latitud,
    longitud,
    beneficio_pedido,
    ventas_cliente,
    margen_ganancia_item,
    cantidad,
    ventas,
    total_item,
    ganancia_pedido,
    riesgo_retraso,
    id_producto,
    id_destino,
    id_ubicacion_cliente
)

SELECT

    R.id_raw,

    R.fecha_pedido,

    R.fecha_envio,

    R.tipo_transaccion,

    R.estado_pedido,

    R.estado_entrega,

    R.modo_envio,

    R.dias_envio_real,

    R.dias_envio_prog,

    R.precio_producto,

    R.precio_base,

    R.latitud,

    R.longitud,

    R.beneficio_pedido,

    R.ventas_cliente,

    R.margen_ganancia_item,

    R.cantidad,

    R.ventas,

    R.total_item,

    R.ganancia_pedido,

    R.riesgo_retraso,

    P.id_producto,

    D.id_destino,

    U.id_ubicacion_cliente

FROM DataCoSupplyChain_RAW R

INNER JOIN Producto P
    ON R.nombre_producto = P.nombre_producto

INNER JOIN Destino D
    ON R.ciudad_destino = D.ciudad_destino
   AND R.estado_destino = D.estado_destino
   AND R.pais_destino = D.pais_destino
   AND R.region_destino = D.region_destino

INNER JOIN UbicacionCliente U
    ON R.ciudad_cliente = U.ciudad_cliente
   AND R.pais_cliente = U.pais_cliente;

COMMIT TRANSACTION;

PRINT 'Carga completada correctamente.';

END TRY

BEGIN CATCH

    ROLLBACK TRANSACTION;

    PRINT ERROR_MESSAGE();

END CATCH;

SELECT COUNT(*) AS TotalPedidos
FROM Pedido;


SELECT
    COUNT(*) AS Total,
    COUNT(id_producto) AS Productos,
    COUNT(id_destino) AS Destinos,
    COUNT(id_ubicacion_cliente) AS Clientes
FROM Pedido;