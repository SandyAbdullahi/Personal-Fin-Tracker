echo "Ensuring the application database exists…"
psql "$(echo "$DATABASE_URL" | sed -E 's|/[^/]+$|/postgres|')" \
     -v dbname="$(echo "$DATABASE_URL" | sed -E 's|^.*/||')" \
     -v dbuser="$DB_USER" <<'SQL'
DO $$
BEGIN
   IF NOT EXISTS (
     SELECT FROM pg_database WHERE datname = :'dbname'
   ) THEN
     PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE ' || quote_ident(:'dbname') ||
                         ' OWNER ' || quote_ident(:'dbuser'));
   END IF;
END;
$$;
SQL
