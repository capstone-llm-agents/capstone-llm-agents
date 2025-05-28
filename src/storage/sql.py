"""SQLMapper class to map serialisable objects to an SQLite database."""

import sqlite3
from typing import Type, List

from core.chat import ChatHistory
from core.entity import Entity
from storage.serialisable import Serialisable


class SQLMapper:
    """A class to map serialisable objects to a table in an SQLite database."""

    def __init__(self, db_path: str, table_name: str):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.table_name = table_name

        # TODO temporary hack
        entity = Entity("example_entity", "An example entity", "example_role")
        chat_history = ChatHistory()

        def create_table_if_not_exists(serialisable_cls: Serialisable):
            table_name = self.table_name
            data = serialisable_cls.to_dict()

            columns = [f"{k} {self._map_python_type(v)}" for k, v in data.items()]
            create_stmt = (
                f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)});"
            )
            self.cursor.execute(create_stmt)

        # Create table if it does not exist
        if table_name == "agents":
            create_table_if_not_exists(entity)
        else:
            create_table_if_not_exists(chat_history)

    def _map_python_type(self, value):
        if isinstance(value, int):
            return "INTEGER"
        elif isinstance(value, float):
            return "REAL"
        elif isinstance(value, bool):
            return "BOOLEAN"
        else:
            return "TEXT"

    def save(self, obj: Serialisable):
        """Save a serialisable object to the database."""
        table_name = self.table_name
        data = obj.to_dict()

        # CREATE TABLE
        columns = [f"{k} {self._map_python_type(v)}" for k, v in data.items()]
        create_stmt = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)});"
        self.cursor.execute(create_stmt)

        # INSERT
        placeholders = ", ".join(["?"] * len(data))
        insert_stmt = f"INSERT INTO {table_name} ({', '.join(data.keys())}) VALUES ({placeholders});"
        self.cursor.execute(insert_stmt, list(data.values()))
        self.conn.commit()

    def load(self, cls: Type[Serialisable]) -> List[Serialisable]:
        """Load all records of a serialisable object from the database."""

        table_name = self.table_name
        select_stmt = f"SELECT * FROM {table_name};"
        self.cursor.execute(select_stmt)

        # Get column names
        columns = [description[0] for description in self.cursor.description]
        rows = self.cursor.fetchall()

        results = []
        for row in rows:
            row_dict = dict(zip(columns, row))
            results.append(cls.from_dict(row_dict))

        return results

    def clear_table(self):
        """Clear the table in the database."""
        table_name = self.table_name
        clear_stmt = f"DELETE FROM {table_name};"
        self.cursor.execute(clear_stmt)
        self.conn.commit()

    def close(self):
        """Close the database connection explicitly."""
        self.cursor.close()
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
