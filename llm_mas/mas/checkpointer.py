import pickle
import sqlite3

from llm_mas.logging.loggers import APP_LOGGER
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
                    state BLOB,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def save(self, state: State):
        """
        json_string = json.dumps(state, indent=4)
        """

        pickled_history = pickle.dumps(state)

        with sqlite3.connect(self.dp_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO agent_state (state) VALUES (?)
                """,
                (pickled_history,),
            )
            conn.commit()

    def fetch(self) -> State | None:
        with sqlite3.connect(self.dp_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT state FROM agent_state ORDER BY id DESC LIMIT 1
                """
            )
            row = cursor.fetchone()
            if row:
                pickle_data = row[0]
                data: State = pickle.loads(pickle_data)
                APP_LOGGER.info(f"Fetched checkpoint data: {data}")
                return data
            else:
                return None
