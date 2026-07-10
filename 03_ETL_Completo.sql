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