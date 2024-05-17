use role useradmin;

-- create functional roles
create or replace role data_scientist;
create or replace role data_engineer;
create or replace role marketing_analyst;
create or replace role sales_analyst;


use role sysadmin;
-- DB: company_db
create or replace database company_db;
-- SCHEMA: RAW, MART
create or replace schema RAW;
create or replace schema MART;
-- Tables: sales, marketing, finance, hr
create or replace table company_db.RAW.sales (id int, date date, product string, price float, quantity int);
create or replace table company_db.RAW.marketing (id int, date date, campaign string, channel string, cost float);
create or replace table company_db.RAW.finance (id int, date date, revenue float, expenses float);
create or replace table company_db.RAW.hr (id int, date date, employee string, department string, salary float);

create or replace table company_db.MART.sales (id int, date date, product string, price float, quantity int);
create or replace table company_db.MART.marketing (id int, date date, campaign string, channel string, cost float);
create or replace table company_db.MART.finance (id int, date date, revenue float, expenses float);
create or replace table company_db.MART.hr (id int, date date, employee string, department string, salary float);

-- create access roles

use role accountadmin;
create or replace role company_raw_read_access;
grant usage on database company_db to role company_raw_read_access;
grant usage on schema company_db.RAW to role company_raw_read_access;
grant select on all tables in schema company_db.RAW to role company_raw_read_access;

create or replace role company_raw_write_access;
grant usage on database company_db to role company_raw_read_access;
grant usage on schema company_db.RAW to role company_raw_read_access;
grant select on all tables in schema company_db.RAW to role company_raw_read_access;
grant insert on all tables in schema company_db.RAW to role company_raw_write_access;
grant update on all tables in schema company_db.RAW to role company_raw_write_access;
grant delete on all tables in schema company_db.RAW to role company_raw_write_access;


create or replace role company_mart_read_access;
grant usage on database company_db to role company_mart_read_access;
grant usage on schema company_db.MART to role company_mart_read_access;
grant select on all tables in schema company_db.MART to role company_mart_read_access;
create or replace role company_mart_write_access;
grant usage on database company_db to role company_mart_write_access;
grant usage on schema company_db.MART to role company_mart_write_access;
grant select on all tables in schema company_db.MART to role company_mart_write_access;
grant insert on all tables in schema company_db.MART to role company_mart_write_access;
grant update on all tables in schema company_db.MART to role company_mart_write_access;
grant delete on all tables in schema company_db.MART to role company_mart_write_access;

create or replace role sales_read_access;
grant usage on database company_db to role sales_read_access;
grant usage on schema company_db.MART to role sales_read_access;
grant select on company_db.MART.sales to role sales_read_access;

create or replace role sales_write_access;
grant usage on database company_db to role sales_write_access;
grant usage on schema company_db.MART to role sales_write_access;
grant select on company_db.MART.sales to role sales_write_access;
grant insert on company_db.MART.sales to role sales_write_access;
grant update on company_db.MART.sales to role sales_write_access;
grant delete on company_db.MART.sales to role sales_write_access;

create or replace role marketing_read_access;
grant usage on database company_db to role marketing_read_access;
grant usage on schema company_db.MART to role marketing_read_access;
grant select on company_db.MART.marketing to role marketing_read_access;

create or replace role marketing_write_access;
grant usage on database company_db to role marketing_write_access;
grant usage on schema company_db.MART to role marketing_write_access;
grant select on company_db.MART.marketing to role marketing_write_access;
grant insert on company_db.MART.marketing to role marketing_write_access;
grant update on company_db.MART.marketing to role marketing_write_access;
grant delete on company_db.MART.marketing to role marketing_write_access;

create or replace role finance_read_access;
grant usage on database company_db to role finance_read_access;
grant usage on schema company_db.MART to role finance_read_access;
grant select on company_db.MART.finance to role finance_read_access;

create or replace role finance_write_access;
grant usage on database company_db to role finance_write_access;
grant usage on schema company_db.MART to role finance_write_access;
grant select on company_db.MART.finance to role finance_write_access;
grant insert on company_db.MART.finance to role finance_write_access;
grant update on company_db.MART.finance to role finance_write_access;
grant delete on company_db.MART.finance to role finance_write_access;



create or replace role hr_read_access;
grant usage on database company_db to role hr_read_access;
grant usage on schema company_db.MART to role hr_read_access;
grant select on company_db.MART.hr to role hr_read_access;

create or replace role hr_write_access;
grant usage on database company_db to role hr_write_access;
grant usage on schema company_db.MART to role hr_write_access;
grant select on company_db.MART.hr to role hr_write_access;
grant insert on company_db.MART.hr to role hr_write_access;
grant update on company_db.MART.hr to role hr_write_access;
grant delete on company_db.MART.hr to role hr_write_access;


-- functional roleへのaccess roleの付与
grant role company_raw_read_access to role data_scientist;
grant role company_raw_read_access to role data_engineer;
grant role company_raw_write_access to role data_engineer;

grant role company_mart_read_access to role data_scientist;
grant role company_mart_read_access to role data_engineer;
grant role company_mart_write_access to role data_engineer;



grant role marketing_read_access to role marketing_analyst;

grant role sales_read_access to role sales_analyst;

show grants to role marketing_analyst;
revoke role COMPANY_RAW_READ_ACCESS from role marketing_analyst;
revoke role COMPANY_MART_READ_ACCESS from role marketing_analyst;

show grants to role sales_analyst;
revoke role COMPANY_RAW_READ_ACCESS from role sales_analyst;
revoke role COMPANY_MART_READ_ACCESS from role sales_analyst;



SHOW GRANTS TO ROLE data_scientist;
SHOW GRANTS TO ROLE data_engineer;
SHOW GRANTS TO ROLE marketing_analyst;
SHOW GRANTS TO ROLE sales_analyst;

-- name, grantee_name, privilege, granted_on
CREATE OR REPLACE TABLE role_info (name string, grantee_name string, privilege string, granted_on string);

SHOW GRANTS TO ROLE data_scientist;
INSERT INTO role_info
SELECT "name", "grantee_name", "privilege", "granted_on"
FROM table(result_scan('01b3c086-0001-5e63-0000-a81d0015110a'));


SHOW GRANTS TO ROLE data_engineer;
INSERT INTO role_info
SELECT "name", "grantee_name", "privilege", "granted_on"
FROM table(result_scan('01b3c086-0001-5e24-0000-a81d001520de'));

SHOW GRANTS TO ROLE marketing_analyst;
INSERT INTO role_info
SELECT "name", "grantee_name", "privilege", "granted_on"
FROM table(result_scan('01b3c086-0001-5e24-0000-a81d001520e6'));

SHOW GRANTS TO ROLE sales_analyst;
INSERT INTO role_info
SELECT "name", "grantee_name", "privilege", "granted_on"
FROM table(result_scan('01b3c086-0001-5e63-0000-a81d0015112e'));


select name from role_info;
show tables like 'role_info';

-- snowflake scriptでrole_infoのnameをloopして、SHOW GRANTS TO ROLE name;を実行する

EXECUTE IMMEDIATE $$
BEGIN
    CREATE OR REPLACE TABLE role_info (name string, grantee_name string, privilege string, granted_on string);
    CREATE OR REPLACE TABLE access_role_functional_role_link (access_role string, functional_role string);

    SHOW GRANTS TO ROLE data_scientist;
    INSERT INTO role_info
    SELECT "name", "grantee_name", "privilege", "granted_on"
    FROM table(result_scan(last_query_id()));

    SHOW GRANTS TO ROLE data_engineer;
    INSERT INTO role_info
    SELECT "name", "grantee_name", "privilege", "granted_on"
    FROM table(result_scan(last_query_id()));

    SHOW GRANTS TO ROLE marketing_analyst;
    INSERT INTO role_info
    SELECT "name", "grantee_name", "privilege", "granted_on"
    FROM table(result_scan(last_query_id()));

    SHOW GRANTS TO ROLE sales_analyst;
    INSERT INTO role_info
    SELECT "name", "grantee_name", "privilege", "granted_on"
    FROM table(result_scan(last_query_id()));

    LET role_c CURSOR FOR SELECT NAME FROM role_info;

    FOR role_name IN role_c DO
        EXECUTE IMMEDIATE 'SHOW GRANTS TO ROLE ' || role_name.name;

        INSERT INTO role_info
        SELECT "name", "grantee_name", "privilege", "granted_on"
        FROM table(result_scan(last_query_id()));

        EXECUTE IMMEDIATE 'SHOW GRANTS ON ROLE ' || role_name.name;
        INSERT INTO access_role_functional_role_link
        SELECT "name", "grantee_name"
        FROM table(result_scan(last_query_id()))
        WHERE "privilege" = 'USAGE';
    END FOR;
END;
$$
;

select * from role_info;
select * from access_role_functional_role_link;


SHOW GRANTS ON ROLE SALES_READ_ACCESS;


select * from role_info where grantee_name in 
            (select name from role_info where grantee_name = 'DATA_SCIENTIST');