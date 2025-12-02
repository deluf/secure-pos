"""
A server-side module for managing JSON and file-based IO operations
"""

import json
import os

import threading
import queue
from typing import Any

import requests

from flask import Flask, request, jsonify, Response
from jsonschema import validate, ValidationError
from werkzeug.datastructures import FileStorage

from shared.address import Address

class Endpoint:
    """
    Represents an API endpoint with a specific URL and an optional schema.

    :ivar url: The URL of the endpoint. Must start with '/'
    :type url: str
    :ivar schema: The optional schema associated with the endpoint
    :type schema: str | None
    """
    def __init__(self, url: str, schema: str | None = None):
        """
        Initializes the class attributes

        :param url: The URL string of the endpoint. Must start with '/'
        :type url: str
        :param schema: The optional JSON validation schema for the endpoint
        :type schema: str | None
        """
        self.url = url
        self.schema = schema

class SystemsIO:
    """
    Manages a Flask-based server for handling JSON and file-based endpoints. Provides functionality
    to send and receive data while maintaining internal queues and schemas for validation

    :ivar queues: Each endpoint has a dedicated queue for incoming data
    :type queues: dict[str, queue.Queue]
    :ivar schemas: Endpoints mapped to JSON validation schemas. Only applicable to JSON endpoints
    :type schemas: dict[str, dict[str, Any]]
    :ivar app: The Flask application instance used for the server
    :type app: Flask
    :ivar port: The port number the server listens to
    :type port: int
    :ivar host: The host address the server listens to
    :type host: str
    """

    def __init__(self, endpoints: list[Endpoint], port: int, host: str = "0.0.0.0"):
        """
        Initializes and configures a Flask-based server

        :param endpoints: List of endpoints to be registered
        :param port: Port number on which the Flask server will listen to
        :param host: (Optional) Host address for the Flask server
        """
        self.app = Flask(__name__)
        self.port = port
        self.host = host
        self.queues: dict[str, queue.Queue] = {}
        self.schemas: dict[str, dict[str, Any]] = {}

        for endpoint in endpoints:
            self.app.add_url_rule(
                endpoint.url,
                endpoint=endpoint.url,
                view_func=self._handle_incoming_request,
                methods=["POST"]
            )
            self.queues[endpoint.url] = queue.Queue()

            if endpoint.schema:
                with open(endpoint.schema, encoding="utf-8") as schema_file:
                    schema = json.load(schema_file)
                self.schemas[endpoint.url] = schema
                print(f"[SystemsIO] Registered JSON endpoint {endpoint.url} with schema {endpoint.schema}")
            else:
                print(f"[SystemsIO] Registered FILE endpoint {endpoint.url}")

        # Start Flask in a background thread
        threading.Thread(
            target=self.app.run,
            kwargs={
                "host": self.host,
                "port": self.port,
                "debug": False,
                "use_reloader": False
            },
            daemon=True
        ).start()
        print(f"[SystemsIO] Flask server started on {self.host}:{self.port}")
        
    def _handle_incoming_request(self) -> tuple[Response, int]:
        """
        Internal Flask route handler for ALL registered endpoints

        :return: A JSON response indicating the success or failure of the request
        """
        if request.is_json:
            path = request.path
            data = request.get_json()
            print(f"[SystemsIO] Received JSON payload: {data}")
            schema = self.schemas.get(path)
            try:
                validate(instance=data, schema=schema)
            except ValidationError as e:
                print(f"[SystemsIO] Schema validation failed on {path}: {e.message}")
                return jsonify({"error": "Schema validation failed", "details": e.message}), 400
            self.queues[path].put(data)
            return jsonify({"status": "Queued"}), 200

        if request.files:
            path = request.path
            received_files = []
            for _, file_storage in request.files.items():
                if file_storage.filename == '':
                    continue  # Skip empty files
                received_files.append(file_storage.filename)
                os.makedirs("csv", exist_ok=True)
                file_storage.save(f"csv/{file_storage.filename}")
                self.queues[path].put(file_storage.filename)
                print(f"[SystemsIO] Received FILE: {file_storage.filename}")
            if not received_files:
                return jsonify({"error": "No valid files found"}), 400
            return jsonify({"status": f"Received: {received_files}"}), 200

        return jsonify({"error": "Unsupported Media Type. Send 'application/json'"
            " or 'multipart/form-data' with files"}), 415

    @staticmethod
    def send_json(target: Address, endpoint: str, data: dict[str, Any]) -> None:
        """
        Sends a JSON payload to a specified target system

        :param target: The target address
        :type target: Address
        :param endpoint: A specified endpoint path. Must start with '/'
        :type endpoint: str
        :param data: The JSON-serializable content to be sent
        :type data: Any
        :return: None
        :raises requests.exceptions.RequestException: If the transmission fails
        """
        url = f"http://{target.ip}:{target.port}{endpoint}"
        requests.post(url, json=data, timeout=None).raise_for_status()

    @staticmethod
    def send_file(target: Address, endpoint: str, file_path: str) -> None:
        """
        Sends a file to a specified endpoint on a target address using an HTTP POST request.

        :param target: An object containing the target's IP address and port information
        :type target: Address
        :param endpoint: The API endpoint where the file will be sent
        :param file_path: The file system path to the file that will be sent
        :return: None
        :raises requests.HTTPError: If the HTTP request fails
        """
        url = f"http://{target.ip}:{target.port}{endpoint}"
        with open(file_path, 'rb') as file:
            requests.post(url, files={file_path: file}, timeout=None).raise_for_status()

    def receive(self, endpoint: str) -> dict[str, Any] | str:
        """
        Retrieve data from the specified endpoint queue.
        Data can be either a JSON object or the path of a file.
        This method blocks indefinitely until data is available

        :param endpoint: The endpoint identifier. Must start with '/'
        :type endpoint: str
        :return: The next available item from the associated endpoint queue
        :rtype: dict[str, Any] | str
        :raises ValueError: If the provided endpoint is not registered
        """
        if endpoint not in self.queues:
            raise ValueError(f"Endpoint '{endpoint}' is not registered. "
                f"Available endpoints are: {list(self.queues.keys())}")
        return self.queues[endpoint].get(block=True)
