from segregation_system.prepared_sessions_db import PreparedSession
from segregation_system_configuration import Address
import requests
import threading
import queue
from flask import Flask, request

class SegregationSystemIO:
    def __init__(
        self,
        port: int,
        messaging_system_address: Address,
        development_system_address: Address
    ):
        self.port = port
        self.messaging_system_address = messaging_system_address
        self.development_system_address = development_system_address

        # Thread-safe queue to hold data received by Flask asynchronously
        self.received_sessions_queue = queue.Queue()
        self.app = Flask(__name__)
        self.app.add_url_rule(
            '/api/prepared-session',
            view_func=self._api_prepared_session,
            methods=['POST']
        )

        # Start Flask in a separate thread
        # (daemon=True ensures the thread dies when the main program exits)
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        print(f"Flask server started on port {self.port} in a background thread")

    def _run_server(self):
        self.app.run(port=self.port, debug=False, use_reloader=False)

    def _api_prepared_session(self):
        if not request.is_json:
            return "", 400

        prepared_session = request.get_json()
        # FIXME: Should validate the JSON schema here

        # Put the data into the queue for the main thread to consume
        self.received_sessions_queue.put(prepared_session)

        print("Received prepared session and added to queue")

        return "", 200

    def receive_prepared_session(self, block=True, timeout=None) -> PreparedSession | None:
        try:
            data = self.received_sessions_queue.get(block=block, timeout=timeout)
            return PreparedSession(**data)
        except queue.Empty:
            return None

    def send_calibration_sets(self, data):
        target_url = f"{self.development_system_address.ip}:{self.development_system_address.port}/api/..."
        try:
            response = requests.post(target_url, json=data)
            response.raise_for_status()
            print(f"Success sending calibration: {response.status_code}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending calibration sets: {e}")
            return None

    def send_data_balancing_results(self, data):
        target_url = f"{self.messaging_system_address.ip}:{self.messaging_system_address.port}/api/..."
        try:
            response = requests.post(target_url, json=data)
            response.raise_for_status()
            print(f"Success sending balancing: {response.status_code}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending balancing results: {e}")
            return None

    def send_data_coverage_results(self, data):
        target_url = f"{self.messaging_system_address.ip}:{self.messaging_system_address.port}/api/..."
        try:
            response = requests.post(target_url, json=data)
            response.raise_for_status()
            print(f"Success sending coverage: {response.status_code}")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error sending coverage results: {e}")
            return None
