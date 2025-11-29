import requests
import threading
import queue
import logging
from flask import Flask, request, jsonify
from typing import Dict, Any, Optional, Type, TypeVar, Union
from dataclasses import is_dataclass, asdict

# UPDATE THIS IMPORT based on your project structure
# Example: from shared.address import Address
from shared.address import Address

# Generic Type Definition for the Receive method
T = TypeVar('T')


class JsonIO:
    """
    Handles JSON communication via HTTP/REST.

    Features:
    - Background Daemon Server: Listens for incoming JSON on a separate thread.
    - Automatic Serialization: Converts @dataclass objects to JSON automatically on send.
    - Automatic Deserialization: Converts JSON to @dataclass objects automatically on receive.
    - Thread-safe: Uses a queue to transfer data from the background server to the main application.
    """

    def __init__(self, listening_port: int, host: str = "0.0.0.0"):
        """
        Initializes the JsonIO system and starts the background Flask server.

        Args:
            listening_port: The port this system should listen on.
            host: The host to bind to (default 0.0.0.0 for all interfaces).
        """
        self.port = listening_port
        self.host = host

        # Thread-safe queue to store incoming JSON payloads
        self._rx_queue = queue.Queue()

        # Configure Flask
        self.app = Flask(__name__)

        # Define the route for receiving data
        # Accepts generic JSON payloads
        self.app.add_url_rule(
            '/api/json',
            view_func=self._handle_incoming_request,
            methods=['POST']
        )

        # Start Flask in a separate daemon thread
        # daemon=True ensures this thread dies when the main program exits
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        print(f"[JsonIO] Background server started on {self.host}:{self.port}")

    def _run_server(self):
        """Internal method to run the Flask app."""
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)

    def _handle_incoming_request(self):
        """Internal Flask route handler."""
        if not request.is_json:
            return jsonify({"error": "Payload must be JSON"}), 400

        data = request.get_json()

        # Put the data into the queue for the main thread to consume
        self._rx_queue.put(data)

        # Acknowledge receipt immediately to the sender
        return jsonify({"status": "queued"}), 200

    def send(self, data: Any, target_address: Address, endpoint: str = "") -> bool:
        """
        Sends data to a target system.

        Args:
            data: The data to send. Can be a Dictionary or a @dataclass.
            target_address: The Address object of the destination.
            endpoint: The specific API endpoint (default is empty, usually goes to root or specified path).

        Returns:
            bool: True if successful, False otherwise.
        """
        # AUTOMATIC CONVERSION: Dataclass -> Dict
        if is_dataclass(data):
            payload = asdict(data)
        else:
            payload = data

        # Format URL
        if endpoint and not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        url = f"{target_address.get_url()}{endpoint}"

        try:
            # print(f"[JsonIO] Sending data to {url}...")
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"[JsonIO] Error sending to {url}: {e}")
            return False

    def receive(self, structure: Type[T] = None, timeout: Optional[float] = None) -> Union[T, Dict, None]:
        """
        Retrieves the next item from the queue. Blocks until data is available.

        Args:
            structure: (Optional) The class type (e.g., MyClass) to convert the JSON into.
                       If None, returns a raw Dictionary.
            timeout: (Optional) Seconds to wait before giving up. None waits indefinitely.

        Returns:
            An instance of 'structure', a Dictionary, or None if timed out.
        """
        try:
            # block=True makes this wait until data is available
            data_dict = self._rx_queue.get(block=True, timeout=timeout)

            # AUTOMATIC CONVERSION: Dict -> Dataclass
            if structure and is_dataclass(structure):
                # Unpacks dictionary into the class constructor
                return structure(**data_dict)

            return data_dict

        except queue.Empty:
            return None