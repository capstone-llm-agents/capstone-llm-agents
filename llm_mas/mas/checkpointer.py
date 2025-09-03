import json
import sqlite3

from llm_mas.mas.agentstate import State



class CheckPointer:
    def __init__(self, dp_path: str):
        self.dp_path = dp_path
        self.create_table_if_not_exists()

    def create_table_if_not_exists(self):
        with sqlite3.connect(self.dp_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_state (
                    id INTEGER PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def save(self, state: State):
        json_string = json.dumps(state, indent=4)
        with sqlite3.connect('test.sqlite') as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO agent_state (state_json) VALUES (?)
                """,
                (json_string,)  # The comma is crucial to make it a tuple!
            )
            conn.commit()

    def fetch(self) -> State | None:

        with sqlite3.connect('test.sqlite') as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT state_json FROM agent_state ORDER BY id DESC LIMIT 1
                """
            )
            row = cursor.fetchone()
            if row:
                json_string = row[0]
                data: State = json.loads(json_string)
                return data
            else:
                return None
