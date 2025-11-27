
import json
from dataclasses import dataclass
import sqlite3

@dataclass
class PreparedSession:
    uuid: str
    mean_absolute_differencing_transaction_timestamps: float
    mean_absolute_differencing_transaction_amount: float
    median_location: float
    median_target_ip: str
    median_dest_ip: str
    label: str

class PreparedSessionsDB:

    def __init__(self, db_path: str = "prepared-sessions.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()

    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS prepared_sessions (
            uuid VARCHAR(32) PRIMARY KEY,
            mad_timestamps REAL,
            mad_amount REAL,
            median_location REAL,
            median_target_ip VARCHAR(15),
            median_dest_ip VARCHAR(15)
        );
        """
        with self.conn:
            self.conn.execute(query)

    def store(self, prepared_session: PreparedSession):
        query = """
        INSERT INTO prepared_sessions (
            uuid,
            mad_timestamps, 
            mad_amount, 
            median_location, 
            median_target_ip, 
            median_dest_ip
        ) VALUES (?, ?, ?, ?, ?, ?)
        """

        values = (
            prepared_session.uuid,
            prepared_session.mean_absolute_differencing_transaction_timestamps,
            prepared_session.mean_absolute_differencing_transaction_amount,
            prepared_session.median_location,
            prepared_session.median_target_ip,
            prepared_session.median_dest_ip
        )

        with self.conn:
            self.conn.execute(query, values)

    def getAll(self) -> list[PreparedSession]:
        query = """
        SELECT 
            uuid,
            mad_timestamps, 
            mad_amount, 
            median_location, 
            median_target_ip, 
            median_dest_ip
        FROM prepared_sessions
        """

        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            session = PreparedSession(
                uuid=row[0],
                mean_absolute_differencing_transaction_timestamps=row[1],
                mean_absolute_differencing_transaction_amount=row[2],
                median_location=row[3],
                median_target_ip=row[4],
                median_dest_ip=row[5]
            )
            results.append(session)
        return results

    def close(self):
        self.conn.close()
