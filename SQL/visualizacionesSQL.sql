SELECT name
FROM sys.server_principals
WHERE type_desc = 'WINDOWS_LOGIN';

CREATE LOGIN [OMEGA-DELL\Jefferson Dell]
FROM WINDOWS;

ALTER SERVER ROLE sysadmin
ADD MEMBER [OMEGA-DELL\Jefferson Dell];

DROP LOGIN [DESKTOP-VS0C39Q\Jefferson Dell];

SELECT
    name,
    SUSER_SNAME(owner_sid) AS Owner
FROM sys.databases;

ALTER AUTHORIZATION
ON DATABASE::BD_ML_RELACIONAL
TO sa;

SELECT SUSER_SNAME(owner_sid)
FROM sys.databases
WHERE name='master';

SELECT @@SERVERNAME;

SELECT SERVERPROPERTY('MachineName');

SELECT @@SERVERNAME AS Servidor;

SELECT
    SERVERPROPERTY('MachineName') AS MachineName,
    SERVERPROPERTY('ServerName') AS ServerName,
    SERVERPROPERTY('InstanceName') AS InstanceName;



    EXEC sp_DatasetML;