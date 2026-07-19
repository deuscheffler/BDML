-- CREACION DE ESQUEMAS

CREATE SCHEMA stg;
GO

CREATE SCHEMA dim;
GO

CREATE SCHEMA fact;
GO

CREATE SCHEMA audit;
GO

CREATE TABLE audit.AuditoriaPedido
(
    id_auditoria INT IDENTITY(1,1) PRIMARY KEY,

    fecha_evento DATETIME NOT NULL DEFAULT(GETDATE()),

    usuario_sql SYSNAME NOT NULL DEFAULT(SUSER_SNAME()),

    tipo_operacion VARCHAR(20),

    id_pedido INT,

    descripcion VARCHAR(500)
);
GO

CREATE OR ALTER TRIGGER TR_AuditoriaPedido

ON Pedido

AFTER INSERT, UPDATE, DELETE

AS
BEGIN

    SET NOCOUNT ON;

    INSERT INTO audit.AuditoriaPedido
    (
        tipo_operacion,
        id_pedido,
        descripcion
    )

    SELECT

        CASE

            WHEN EXISTS(SELECT * FROM inserted)
             AND EXISTS(SELECT * FROM deleted)

                THEN 'UPDATE'

            WHEN EXISTS(SELECT * FROM inserted)

                THEN 'INSERT'

            ELSE 'DELETE'

        END,

        COALESCE(i.id_pedido,d.id_pedido),

        'Operación registrada automáticamente'

    FROM inserted i

    FULL OUTER JOIN deleted d

    ON i.id_pedido=d.id_pedido;

END;
GO

UPDATE Pedido

SET ventas = ventas

WHERE id_pedido = 1;

SELECT TOP 10 *

FROM audit.AuditoriaPedido

ORDER BY id_auditoria DESC;

-- ROLES
CREATE ROLE Administrador;
GO

CREATE ROLE Analista;
GO

ALTER ROLE Administrador
ADD MEMBER dbo;

GRANT SELECT
ON vw_ML_DataCoSupplyChain
TO Analista;
GO

GRANT EXECUTE
ON sp_DatasetML
TO Analista;
GO

GRANT EXECUTE
ON sp_EstadisticasML
TO Analista;
GO
