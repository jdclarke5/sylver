"""PostgreSQL backend."""

from .backend import BaseBackend

import psycopg2
from psycopg2 import sql

class PostgresBackend(BaseBackend):

    def __init__(self, connection_string):
        """Initialise PostgreSQL connection with a valid libpq connection 
        string. Create the `position`, `status`, and `reply` tables if they
        do not yet exist.
        """
        self.conn = psycopg2.connect(connection_string)
        with self.conn:
            with self.conn.cursor() as c:
                c.execute("""
                    CREATE TABLE IF NOT EXISTS position (
                        name            text        PRIMARY KEY,
                        generators      integer[]   NOT NULL,
                        gcd             integer     NOT NULL,
                        multiplicity    integer     NOT NULL,
                        genus           integer     NOT NULL,
                        frobenius       integer     NOT NULL,
                        irreducible     char (1)    NULL
                    );""")
                c.execute("""
                    CREATE TABLE IF NOT EXISTS status (
                        position        text        PRIMARY KEY,
                        status          varchar (2) NOT NULL
                    );""")
                c.execute("""
                    CREATE TABLE IF NOT EXISTS reply (
                        position        text        NOT NULL,
                        reply           integer     NOT NULL,
                        CONSTRAINT uniquetuple UNIQUE (position, reply)
                    );""")
        self.position_cols = ("name", "generators", "gcd", "multiplicity",
            "genus", "frobenius", "irreducible")

    def save(self, position, status, replies):
        """PostgreSQL implementation of BaseBackend method.
        """
        position_dict = {"name": position.name, **position.to_dict()}
        # Position
        columns = sql.SQL(",").join(map(sql.Identifier, self.position_cols))
        values = sql.SQL(",").join(map(sql.Placeholder, self.position_cols))
        position_query = sql.SQL("""
            INSERT INTO position ({columns}) VALUES ({values}) 
            ON CONFLICT (name) DO NOTHING;""").format(
                columns=columns, values=values)
        # Status
        status_query = sql.SQL("""
            INSERT INTO status (position, status) VALUES (%(name)s, {status})
            ON CONFLICT (position) DO UPDATE SET status = EXCLUDED.status
            WHERE status.status != 'P' AND status.status != 'N';
        """).format(status=sql.Literal(status))
        # Reply
        reply_values = [sql.SQL("(%(name)s, {})").format(sql.Literal(r))
            for r in replies]
        reply_query = sql.SQL("""
            INSERT INTO reply (position, reply) VALUES {}
            ON CONFLICT ON CONSTRAINT uniquetuple DO NOTHING;
        """).format(sql.SQL(",").join(reply_values))
        with self.conn:
            with self.conn.cursor() as c:
                c.execute(position_query, position_dict)
                c.execute(status_query, position_dict)
                if replies:
                    c.execute(reply_query, position_dict)
    
    def get_status(self, position):
        """PostgreSQL implementation of BaseBackend method.
        """
        query = "SELECT status FROM status WHERE position = %(name)s;"
        with self.conn:
            with self.conn.cursor() as c:
                c.execute(query, {"name": position.name})
                result = c.fetchone()
        return result[0] if result else None
