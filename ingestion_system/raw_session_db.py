import sqlite3
import json
from typing import Optional, Dict

from ingestion_system.raw_session import RawSession


class RawSessionDB:
    def __init__(self, db_path: str = "raw_sessions.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        # We store the 3 distinct parts. Each part contains lists of 10 samples.
        query = """
                CREATE TABLE IF NOT EXISTS partial_sessions \
                ( \
                    uuid \
                    VARCHAR \
                ( \
                    32 \
                ) PRIMARY KEY,
                    transaction_data TEXT, -- JSON blob: {timestamp: [...], amount: [...]}
                    network_data TEXT, -- JSON blob: {source_ip: [...], dest_ip: [...]}
                    location_data TEXT, -- JSON blob: {longitude: [...], latitude: [...]}
                    label INTEGER
                    ); \
                """
        with self.conn:
            self.conn.execute(query)

    def store(self, r: dict):
        """
        Stores a partial record. Identifies which of the 3 systems sent it.
        """

        # Identify the source system based on the unique keys defined in the PDF
        sys_col = None
        if 'timestamp' in r:
            sys_col = 'transaction_data'
        elif 'amount' in r:
            sys_col = 'transaction_data'
        elif 'source_ip' in r:
            sys_col = 'network_data'
        elif 'dest_ip' in r:
            sys_col = 'network_data'
        elif 'latitude' in r:
            sys_col = 'location_data'
        elif 'longitude' in r:
            sys_col = 'location_data'

        label_val = r.get('label')
        uuid = r.get('uuid')

        with self.conn:
            # Create row if it doesn't exist
            self.conn.execute("INSERT OR IGNORE INTO partial_sessions (uuid) VALUES (?)", (uuid,))

            # Update the specific system column with the raw JSON data
            if sys_col:
                self.conn.execute(f"UPDATE partial_sessions SET {sys_col} = ? WHERE uuid = ?",
                                  (json.dumps(r), uuid))

            # Update label if present (Development/Evaluation phase) [cite: 144]
            if label_val is not None:
                self.conn.execute("UPDATE partial_sessions SET label = ? WHERE uuid = ?", (label_val, uuid))

        print(f"[RawSessionDB] Stored partial data for UUID {uuid}.")

    def get_complete_session(self, uuid: str) -> RawSession | None:
        """
        Returns the session ONLY if all 3 parts are present.
        It allows incomplete lists (e.g. <10 samples) inside the parts.
        """
        query = "SELECT transaction_data, network_data, location_data, label FROM partial_sessions WHERE uuid = ?"
        cursor = self.conn.cursor()
        cursor.execute(query, (uuid,))
        row = cursor.fetchone()

        if not row: return None

        trans_blob, net_blob, loc_blob, label = row

        # STRICT CHECK: All 3 parts must be present (Not NULL)
        if not all([trans_blob, net_blob, loc_blob]):
            return None

        # Deserialize (If data is incomplete/short inside, we still accept it here)
        t_data = json.loads(trans_blob)
        n_data = json.loads(net_blob)
        l_data = json.loads(loc_blob)

        # Merge into one dictionary
        return RawSession(
            uuid=uuid,
            timestamp=t_data.get('timestamp', []),
            amount=t_data.get('amount', []),
            source_ip=n_data.get('source_ip', []),
            dest_ip=n_data.get('dest_ip', []),
            longitude=l_data.get('longitude', []),
            latitude=l_data.get('latitude', []),
            label=label
        )

    def remove(self, uuid: str):
        with self.conn:
            self.conn.execute("DELETE FROM partial_sessions WHERE uuid = ?", (uuid,))
        print(f"[RawSessionDB] Buffer cleared for {uuid}.")