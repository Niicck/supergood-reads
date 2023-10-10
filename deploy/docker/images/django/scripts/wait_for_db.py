import os
import sys
import time

import psycopg2

suggest_unrecoverable_after = 30
start = time.time()

while True:
    try:
        if os.environ.get("DATABASE_URL"):
            psycopg2.connect(os.environ["DATABASE_URL"])
        else:
            psycopg2.connect(
                dbname=os.environ["DATABASE_NAME"],
                user=os.environ["DATABASE_USER"],
                password=os.environ["DATABASE_PASSWORD"],
                host=os.environ["DATABASE_HOST"],
                port=int(os.environ["DATABASE_PORT"]),
            )
        break
    except psycopg2.OperationalError as error:
        sys.stderr.write("Waiting for PostgreSQL to become available...\n")

        if time.time() - start > suggest_unrecoverable_after:
            sys.stderr.write(
                "  This is taking longer than expected. The following exception may be indicative of an unrecoverable error: '{}'\n".format(
                    error
                )
            )

    time.sleep(1)
