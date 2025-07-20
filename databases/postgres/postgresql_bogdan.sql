
--Create tables:
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT,
    role TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users_audit (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by TEXT,
    field_changed TEXT,
    old_value TEXT,
    new_value TEXT
);

-----------------------------------------------------------------

--create function
CREATE OR REPLACE FUNCTION log_user_update()
RETURNS TRIGGER AS $$
BEGIN
    --change if name
    IF NEW.name IS DISTINCT FROM OLD.name THEN
        INSERT INTO users_audit (user_id, changed_by, field_changed, old_value, new_value)
        VALUES (OLD.id, user, 'name', OLD.name, NEW.name);
    END IF;

    --change if email
    IF NEW.email IS DISTINCT FROM OLD.email THEN
        INSERT INTO users_audit(user_id, changed_by, field_changed, old_value, new_value)
        VALUES (OLD.id, user, 'email', OLD.email, NEW.email);
    END IF;

    --change if role
    IF NEW.role IS DISTINCT FROM OLD.role THEN
        INSERT INTO users_audit(user_id, changed_by, field_changed, old_value, new_value)
        VALUES (OLD.id, user, 'role', OLD.role, NEW.role);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


--create Trigger
CREATE TRIGGER trigger_users_audit
AFTER UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION log_user_update();


--------------------------------------------------------
--create pg_cron
CREATE EXTENSION IF NOT EXISTS pg_cron;

--check if pg_cron is external and his actual version
SELECT extname, extversion FROM pg_extension WHERE extname = 'pg_cron';


--create function which write records into csv file
CREATE OR REPLACE FUNCTION users_audit_export_csv()
RETURNS void
LANGUAGE plpgsql
AS $func$
DECLARE
    fpath text := format(
        '/tmp/users_audit_export_%s.csv',
        to_char(current_date, 'YYYY-MM-DD')
    );
BEGIN
    EXECUTE format($copy$
        COPY (
            SELECT *
            FROM   users_audit
            WHERE  changed_at >= date_trunc(
                       'day',
                       timezone('Europe/Warsaw', now())
                   )
        ) TO %L WITH (FORMAT csv, HEADER true)
    $copy$,
    fpath);
END;
$func$;

--check if data export to csv
SELECT users_audit_export_csv()
------------------------------------------------------------
--create schedule
SELECT cron.schedule('daily_users_audit_export_csv', '0 3 * * *', $$SELECT users_audit_export_csv();$$);

--check cron job
SELECT jobid, schedule, active
FROM   cron.job
WHERE  jobname = 'daily_users_audit_export_csv'

-------------------------------------------------------------
--test records
INSERT INTO users (name,           email,                       role)
VALUES
  ('Alice Brown',   'alice.brown@example.com',   'editor'),
  ('Bruno Rossi',   'bruno.rossi@example.net',   'viewer'),
  ('Chloé Dubois',  'chloe.dubois@example.org',  'admin'),
  ('Diego García',  'd.garcia@example.com',      'viewer'),
  ('Elisa Novak',   'elisa.novak@example.net',   'editor');

-- some small user changes
UPDATE users
SET    email = 'alice.b@example.com'
WHERE  name  = 'Alice Brown';

UPDATE users
SET    role = 'editor'
WHERE  name = 'Bruno Rossi';

UPDATE users
SET    email = 'diego.garcia@corp.com',
       role  = 'admin'
WHERE  name  = 'Diego García';

UPDATE users
SET    name = 'Elisa Nowak'
WHERE  email = 'elisa.novak@example.net';

UPDATE users
SET    role = 'reviewer'
WHERE  role = 'viewer';