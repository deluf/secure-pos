"""
A module for managing a database of prepared sessions
"""

from dataclasses import dataclass
import sqlite3

from shared.attack_risk_level import AttackRiskLevel

@dataclass
class PreparedSession:
    """
    Represents a collection of features ready to be used as inputs to a classifier

    :ivar uuid: Unique identifier for the session
    :type uuid: str
    :ivar mad_timestamps: Median absolute deviation of the transaction timestamps
    :type mad_timestamps: float
    :ivar mad_amounts: Median absolute deviation of the transaction amounts
    :type mad_amounts: float
    :ivar median_longitude: Median longitude value
    :type median_longitude: float
    :ivar median_latitude: Median latitude value
    :type median_latitude: float
    :ivar median_source_ip: Median source IP address
    :type median_source_ip: int
    :ivar median_destination_ip: Median destination IP address
    :type median_destination_ip: int
    :ivar label: Attack risk level associated with the session, if available
    :type label: AttackRiskLevel | None
    """
    uuid: str
    mad_timestamps: float
    mad_amounts: float
    median_longitude: float
    median_latitude: float
    median_source_ip: int
    median_destination_ip: int
    label: AttackRiskLevel | None

class PreparedSessionsDB:
    """
    Manages a database for storing and retrieving prepared sessions

    :ivar database_name: The name of the SQLite database file
    :type database_name: str
    :ivar conn: The active SQLite connection used to communicate with the database
    :type conn: sqlite3.Connection
    """

    def __init__(self, database_name: str = "prepared_sessions.db"):
        """
        Initializes the database and sets up the schema

        :param database_name: The name of the database file to use
        :type database_name: str
        """
        self.database_name = database_name
        self.conn = sqlite3.connect(self.database_name)
        self._create_schema()

    def _create_schema(self):
        """
        Creates the `prepared_sessions` table in the database if it does not already exist

        :return: None
        """
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
        """
        Stores a prepared session into the database

        :param prepared_session: The prepared session to be stored
        :type prepared_session: PreparedSession
        :return: None
        """
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
            prepared_session.mad_timestamps,
            prepared_session.mad_amounts,
            prepared_session.median_longitude,
            prepared_session.median_latitude,
            prepared_session.median_source_ip,
            prepared_session.median_destination_ip,
            prepared_session.label
        )

        with self.conn:
            self.conn.execute(query, values)

    def get_all(self) -> list[PreparedSession]:
        """
        Retrieves all prepared sessions from the database

        :return: A list of prepared sessions
        :rtype: list[PreparedSession]
        """
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
                mad_timestamps=row[1],
                mad_amounts=row[2],
                median_longitude=row[3],
                median_latitude=row[4],
                median_source_ip=row[5],
                median_destination_ip = row[6],
                label = row[7]
            )
            results.append(session)
        return results

    def delete_all(self) -> None:
        """
        Deletes all prepared sessions from the database

        :return: None
        """
        query = "DELETE FROM prepared_sessions"

        with self.conn:
            self.conn.execute(query)
