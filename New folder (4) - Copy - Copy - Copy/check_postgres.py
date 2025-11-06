#!/usr/bin/env python3
"""
Script to help check PostgreSQL connection details
"""

import psycopg2
import os
from dotenv import load_dotenv

def test_postgres_connection():
    """Find the correct database and confirm the employees table exists.

    Strategy:
    1) Connect to the maintenance DB 'postgres' using creds from .env (or fallbacks)
    2) Discover available databases
    3) Try DBs in priority order to find one containing public.employees
    """

    load_dotenv()

    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    user = os.getenv('DB_USER', 'postgres')
    password = os.getenv('DB_PASSWORD', '')
    env_db = os.getenv('DB_NAME')

    configs = [
        {'host': host, 'port': port, 'database': 'postgres', 'user': user, 'password': password},
        {'host': host, 'port': port, 'database': 'postgres', 'user': 'postgres', 'password': password or '123'},
    ]

    print("Testing PostgreSQL connection...")
    print("=" * 50)

    for cfg in configs:
        try:
            print(f"Trying: host={cfg['host']} port={cfg['port']} user={cfg['user']} db={cfg['database']}")
            conn = psycopg2.connect(**cfg)
            cur = conn.cursor()
            cur.execute("SELECT version();")
            print("Connected:", cur.fetchone()[0])

            # collect candidate DB names
            cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
            dbs = [r[0] for r in cur.fetchall()]
            priority = []
            # prioritize env DB and common names
            for name in [env_db, 'employee_db', 'employees', 'mydb', 'postgres']:
                if name and name in dbs and name not in priority:
                    priority.append(name)
            # then add the rest
            for d in dbs:
                if d not in priority:
                    priority.append(d)

            # find DB containing public.employees
            for dbname in priority:
                try:
                    sub = psycopg2.connect(host=cfg['host'], port=cfg['port'], database=dbname, user=cfg['user'], password=cfg['password'])
                    subc = sub.cursor()
                    subc.execute("""
                        SELECT EXISTS (
                          SELECT 1 FROM information_schema.tables
                          WHERE table_schema='public' AND table_name='employees'
                        );
                    """)
                    exists = subc.fetchone()[0]
                    if exists:
                        print(f"\nSUCCESS: Found table public.employees in database: {dbname}")
                        print("Use these settings in your .env:")
                        print(f"DB_HOST={cfg['host']}")
                        print(f"DB_PORT={cfg['port']}")
                        print(f"DB_NAME={dbname}")
                        print(f"DB_USER={cfg['user']}")
                        print(f"DB_PASSWORD={cfg['password']}")
                        subc.close(); sub.close(); cur.close(); conn.close()
                        return True
                    subc.close(); sub.close()
                except psycopg2.Error as e:
                    print(f"Checked {dbname}: {e}")

            cur.close(); conn.close()
        except psycopg2.Error as e:
            print("Failed:", e)
            continue


        

    print("\nCould not find a database containing public.employees.")
    print("- Ensure the table exists (schema 'public', name 'employees')")
    print("- Or update .env DB_NAME to the database shown in pgAdmin that holds this table")
    return False

if __name__ == "__main__":
    test_postgres_connection()
