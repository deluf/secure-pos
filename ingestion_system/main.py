from flask import Flask, request, jsonify
from ingestion_system.ingestion_system_controller import IngestionSystemController

app = Flask(__name__)
controller = IngestionSystemController()


@app.route('/record', methods=['POST'])
def receive_record():
    record = request.get_json()
    if not record:
        return jsonify({"error": "No data"}), 400

    # Trigger: Record Received -> Delegate to Controller
    result = controller.run(record)
    return jsonify(result), 200


@app.route('/config', methods=['PUT'])
def update_config():
    """
    Endpoint to update configuration dynamically.
    Expects JSON: {"missingSamplesThreshold": 0.2, "minimumRecords": 10, ...}
    """
    new_config = request.get_json()
    controller.config.update(new_config)
    return jsonify({"status": "Configuration updated", "config": controller.config.__dict__}), 200


if __name__ == '__main__':
    print("Starting Ingestion System on port 5002...")
    app.run(host='0.0.0.0', port=5002, debug=True)