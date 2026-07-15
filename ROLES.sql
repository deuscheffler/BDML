-- ============================================================================
-- ROLES DE BASE DE DATOS Y PERMISOS (GRANT/REVOKE)
-- BD_ML_RELACIONAL
-- ============================================================================
-- Se crean 3 roles con responsabilidades separadas (principio de mínimo
-- privilegio):
--   rol_analitico    -> solo lectura. Para Streamlit, dashboards, reportes.
--   rol_servicio_ml  -> lectura completa + escritura SOLO en la tabla de
--                        resultados del modelo no supervisado. Para los
--                        scripts de entrenamiento (KMEANSCERCER_corregido.py).
--   rol_admin        -> control total. Para administración del esquema.
-- ============================================================================

USE BD_ML_RELACIONAL;
GO

-- ============================================================================
-- 1) CREACIÓN DE ROLES
-- ============================================================================
CREATE ROLE rol_analitico;
GO
CREATE ROLE rol_servicio_ml;
GO
CREATE ROLE rol_admin;
GO

-- ============================================================================
-- 2) PERMISOS: rol_analitico (SOLO LECTURA)
-- ============================================================================
GRANT SELECT ON dbo.vw_ML_DataCoSupplyChain      TO rol_analitico;
GRANT SELECT ON dbo.Pedido                        TO rol_analitico;
GRANT SELECT ON dbo.Producto                      TO rol_analitico;
GRANT SELECT ON dbo.Categoria                     TO rol_analitico;
GRANT SELECT ON dbo.Destino                       TO rol_analitico;
GRANT SELECT ON dbo.UbicacionCliente              TO rol_analitico;
GRANT SELECT ON dbo.ResultadoModeloNoSupervisado  TO rol_analitico;

GRANT EXECUTE ON dbo.sp_DatasetML             TO rol_analitico;
GRANT EXECUTE ON dbo.sp_BuscarPedidoPorId     TO rol_analitico;
GRANT EXECUTE ON dbo.sp_ResumenVentasPorPais  TO rol_analitico;
GRANT EXECUTE ON dbo.sp_PedidosPorFecha       TO rol_analitico;
GRANT EXECUTE ON dbo.sp_EstadisticasML        TO rol_analitico;

-- Bloqueo explícito de escritura, por si en el futuro alguien lo agrega
-- por error a un rol con permisos de escritura heredados.
DENY INSERT, UPDATE, DELETE, ALTER ON dbo.Pedido                       TO rol_analitico;
DENY INSERT, UPDATE, DELETE, ALTER ON dbo.Producto                     TO rol_analitico;
DENY INSERT, UPDATE, DELETE, ALTER ON dbo.Categoria                    TO rol_analitico;
DENY INSERT, UPDATE, DELETE, ALTER ON dbo.Destino                      TO rol_analitico;
DENY INSERT, UPDATE, DELETE, ALTER ON dbo.UbicacionCliente             TO rol_analitico;
DENY INSERT, UPDATE, DELETE, ALTER ON dbo.ResultadoModeloNoSupervisado TO rol_analitico;
GO

-- ============================================================================
-- 3) PERMISOS: rol_servicio_ml (lectura completa + escritura acotada)
-- ============================================================================
GRANT SELECT ON dbo.vw_ML_DataCoSupplyChain TO rol_servicio_ml;
GRANT EXECUTE ON dbo.sp_DatasetML           TO rol_servicio_ml;

-- Necesita SELECT/INSERT/DELETE + ALTER (SQL Server exige ALTER para poder
-- ejecutar TRUNCATE TABLE) únicamente sobre la tabla de resultados de ML,
-- que es la única que este rol debe modificar.
GRANT SELECT, INSERT, DELETE, ALTER ON dbo.ResultadoModeloNoSupervisado TO rol_servicio_ml;

-- Explícitamente NO puede tocar las tablas maestras del ETL.
DENY INSERT, UPDATE, DELETE, ALTER ON dbo.Pedido           TO rol_servicio_ml;
DENY INSERT, UPDATE, DELETE, ALTER ON dbo.Producto         TO rol_servicio_ml;
DENY INSERT, UPDATE, DELETE, ALTER ON dbo.Categoria        TO rol_servicio_ml;
DENY INSERT, UPDATE, DELETE, ALTER ON dbo.Destino          TO rol_servicio_ml;
DENY INSERT, UPDATE, DELETE, ALTER ON dbo.UbicacionCliente TO rol_servicio_ml;
GO

-- ============================================================================
-- 4) PERMISOS: rol_admin (control total del esquema y los datos)
-- ============================================================================
-- Se apoya en el rol fijo db_owner en vez de listar permiso por permiso:
-- cualquier miembro de rol_admin hereda control total de la base de datos
-- (DDL, DML, gestión de roles, backups, etc.).
ALTER ROLE db_owner ADD MEMBER rol_admin;
GO

-- ============================================================================
-- 5) CREACIÓN DE LOGINS/USUARIOS DE EJEMPLO Y ASIGNACIÓN A ROLES
-- ============================================================================
-- Opción A: autenticación SQL Server (usuario/contraseña)
-- Cambia las contraseñas antes de usar esto en un entorno real.

CREATE LOGIN login_analista WITH PASSWORD = 'CambiaEstaClave_123!';
CREATE USER usuario_analista FOR LOGIN login_analista;
ALTER ROLE rol_analitico ADD MEMBER usuario_analista;
GO

CREATE LOGIN login_servicio_ml WITH PASSWORD = 'CambiaEstaClave_456!';
CREATE USER usuario_servicio_ml FOR LOGIN login_servicio_ml;
ALTER ROLE rol_servicio_ml ADD MEMBER usuario_servicio_ml;
GO

CREATE LOGIN login_admin_bd WITH PASSWORD = 'CambiaEstaClave_789!';
CREATE USER usuario_admin_bd FOR LOGIN login_admin_bd;
ALTER ROLE rol_admin ADD MEMBER usuario_admin_bd;
GO

-- Opción B: autenticación integrada de Windows (equivalente a lo que ya
-- usan tus scripts con trusted_connection=yes), por si prefieres esto en
-- vez de logins SQL:
--
-- CREATE LOGIN [DOMINIO\usuario_analista] FROM WINDOWS;
-- CREATE USER [DOMINIO\usuario_analista] FOR LOGIN [DOMINIO\usuario_analista];
-- ALTER ROLE rol_analitico ADD MEMBER [DOMINIO\usuario_analista];

-- ============================================================================
-- 6) EJEMPLO DE REVOKE (revertir un permiso ya otorgado)
-- ============================================================================
-- Ejemplo: si más adelante rol_analitico no debe poder ver estadísticas
-- agregadas de ML, se revierte así (no rompe los demás permisos del rol):
--
-- REVOKE EXECUTE ON dbo.sp_EstadisticasML FROM rol_analitico;

-- ============================================================================
-- 7) VERIFICACIÓN — permisos efectivos por rol
-- ============================================================================
SELECT
    dp.state_desc,
    dp.permission_name,
    OBJECT_NAME(dp.major_id) AS objeto,
    pr.name AS rol
FROM sys.database_permissions dp
INNER JOIN sys.database_principals pr
    ON dp.grantee_principal_id = pr.principal_id
WHERE pr.name IN ('rol_analitico', 'rol_servicio_ml', 'rol_admin')
ORDER BY rol, objeto;
GO