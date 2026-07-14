-- CREAR LA VISTA PARA ANALIZAR CON PYTHON

CREATE OR ALTER VIEW vw_ML_DataCoSupplyChain
AS
SELECT

    P.id_pedido,
    P.id_raw,

    P.fecha_pedido,
    P.fecha_envio,

    P.estado_pedido,
    P.estado_entrega,
    P.tipo_transaccion,
    P.modo_envio,

    P.dias_envio_real,
    P.dias_envio_prog,

    P.precio_producto,
    P.precio_base,

    P.beneficio_pedido,
    P.ventas_cliente,
    P.margen_ganancia_item,
    P.cantidad,
    P.ventas,
    P.total_item,
    P.ganancia_pedido,

    P.riesgo_retraso,

    P.latitud,
    P.longitud,

    C.nombre_categoria,

    PR.nombre_producto,

    U.ciudad_cliente,
    U.pais_cliente,

    D.ciudad_destino,
    D.estado_destino,
    D.pais_destino,
    D.region_destino

FROM Pedido P

INNER JOIN Producto PR
ON P.id_producto = PR.id_producto

INNER JOIN Categoria C
ON PR.id_categoria = C.id_categoria

INNER JOIN Destino D
ON P.id_destino = D.id_destino

INNER JOIN UbicacionCliente U
ON P.id_ubicacion_cliente = U.id_ubicacion_cliente;
GO

SELECT TOP 10 *
FROM vw_ML_DataCoSupplyChain;

SELECT COUNT(*) AS Total
FROM vw_ML_DataCoSupplyChain;


CREATE OR ALTER VIEW vw_ResumenPedidos
AS
SELECT

    estado_pedido,

    COUNT(*) AS total_pedidos,

    SUM(ventas) AS ventas_totales,

    SUM(ganancia_pedido) AS ganancia_total,

    AVG(dias_envio_real) AS promedio_dias_envio

FROM Pedido

GROUP BY estado_pedido;
GO


SELECT *
FROM vw_ResumenPedidos;