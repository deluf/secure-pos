
from dataclasses import dataclass
import sqlite3

from shared.attack_risk_level import AttackRiskLevel


@dataclass
class PreparedSession:
    uuid: str
    mad_timestamps: float
    mad_amounts: float
    median_longitude: float
    median_latitude: float
    median_source_ip: int
    median_destination_ip: int
    label: AttackRiskLevel | None = None

class PreparedSessionsDB:

    def __init__(self, db_path: str = "prepared_sessions.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()

    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS prepared_sessions (
            uuid VARCHAR(32) PRIMARY KEY,
            mad_timestamps REAL,
            mad_amounts REAL,
            median_longitude REAL,
            median_latitude REAL,
            median_source_ip INTEGER,
            median_destination_ip INTEGER,
            label VARCHAR(32)
        );
        """
        with self.conn:
            self.conn.execute(query)

    def store(self, prepared_session: PreparedSession):
        query = """
        INSERT INTO prepared_sessions (
            uuid,
            mad_timestamps, 
            mad_amounts, 
            median_longitude, 
            median_latitude,
            median_source_ip, 
            median_destination_ip,
            label
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        values = (
            prepared_session.uuid,
            prepared_session.mad_amounts,
            prepared_session.mad_timestamps,
            prepared_session.median_longitude,
            prepared_session.median_latitude,
            prepared_session.median_source_ip,
            prepared_session.median_destination_ip,
            prepared_session.label
        )

        with self.conn:
            self.conn.execute(query, values)

    def getAll(self) -> list[PreparedSession]:
        query = """
        SELECT *
        FROM prepared_sessions
        """

        cursor = self.conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        results = []
        for row in rows:
            session = PreparedSession(
                uuid=row[0],
                mad_amounts=row[1],
                mad_timestamps=row[2],
                median_longitude=row[3],
                median_latitude=row[4],
                median_source_ip=row[5],
                median_destination_ip = row[6],
                label = row[7]
            )
            results.append(session)
        return results

    def close(self):
        self.conn.close()
