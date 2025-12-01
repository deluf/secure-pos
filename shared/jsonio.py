import requests
import threading
import queue
from flask import Flask, request, jsonify
from typing import Dict, Any, Optional, List
from jsonschema import validate, ValidationError
from shared.address import Address

class JsonIO:
    """
    Handles JSON communication via HTTP/REST with multiple endpoint support
    and strict Schema Validation.
    """

    def __init__(self, endpoint_schemas: Dict[str, Optional[Dict]], listening_port: int, host: str = "0.0.0.0"):
        """
        Initializes the JsonIO system and starts the background Flask server.

        Args:
            endpoint_schemas: A dictionary mapping URL paths to JSON Schemas.
                              Format: { '/path': {schema_dict}, '/other': None }
                              If value is None, no validation occurs for that endpoint.
            listening_port: The port this system should listen on.
            host: The host to bind to (default 0.0.0.0).
        """
        self.port = listening_port
        self.host = host

        # Dictionary to hold a queue for each specific endpoint
        self._queues: Dict[str, queue.Queue] = {}

        # Dictionary to hold the schema for each endpoint
        self._schemas: Dict[str, Optional[Dict]] = {}

        # Configure Flask
        self.app = Flask(__name__)

        # Register routes, queues, and schemas
        for ep, schema in endpoint_schemas.items():
            # Ensure endpoint starts with '/' for consistency
            normalized_ep = ep if ep.startswith("/") else f"/{ep}"

            # 1. Create a queue
            self._queues[normalized_ep] = queue.Queue()

            # 2. Store the schema
            self._schemas[normalized_ep] = schema

            # 3. Add the URL rule to Flask
            self.app.add_url_rule(
                normalized_ep,
                endpoint=normalized_ep,
                view_func=self._handle_incoming_request,
                methods=['POST']
            )
            print(f"[JsonIO] Registered endpoint: {normalized_ep} (Schema: {'Yes' if schema else 'No'})")

        # Start Flask in a separate daemon thread
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        print(f"[JsonIO] Background server started on {self.host}:{self.port}")

    def _run_server(self):
        """Internal method to run the Flask app."""
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)

    def _handle_incoming_request(self):
        """Internal Flask route handler for ALL registered endpoints."""
        if not request.is_json:
            return jsonify({"error": "Payload must be JSON"}), 400

        # Identify which endpoint was called
        path = request.path

        if path not in self._queues:
            return jsonify({"error": f"Endpoint {path} not configured"}), 404

        data = request.get_json()

        # --- SCHEMA VALIDATION ---
        schema = self._schemas.get(path)
        if schema:
            try:
                validate(instance=data, schema=schema)
            except ValidationError as e:
                # Validation failed: Do NOT enqueue
                error_msg = f"Schema validation failed: {e.message}"
                print(f"[JsonIO] Rejected request on {path}: {error_msg}")
                return jsonify({"error": "Schema Validation Failed", "details": e.message}), 400
        # -------------------------

        # Route data to the specific queue for this path
        self._queues[path].put(data)

        return jsonify({"status": "queued", "endpoint": path}), 200

    def send(self, data: Dict[str, Any], target_address: Address, endpoint: str = "") -> bool:
        """
        Sends a dictionary as JSON to a target system.
        """
        if endpoint and not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"

        url = f"{target_address.get_url()}{endpoint}"

        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"[JsonIO] Error sending to {url}: {e}")
            return False

    def receive(self, endpoint: str, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Retrieves the next JSON object from the queue associated with the specific endpoint.
        """
        normalized_ep = endpoint if endpoint.startswith("/") else f"/{endpoint}"

        if normalized_ep not in self._queues:
            raise ValueError(f"Endpoint '{normalized_ep}' is not registered. Available: {list(self._queues.keys())}")

        try:
            return self._queues[normalized_ep].get(block=True, timeout=timeout)
        except queue.Empty:
            return None