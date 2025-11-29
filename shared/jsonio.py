import requests
from typing import Dict, Any, Optional
from shared.address import Address


class JsonIO:
    """
    Handles JSON communication between systems via HTTP/REST.

    Ref: UML Class Diagram (Ingestion & Classification)
    """

    def send(self, data: Dict[str, Any], target_address: Address, endpoint: str = "") -> bool:
        """
        Sends a JSON payload to a target system.

        Args:
            data: The dictionary to send as JSON.
            target_address: The Address object of the destination.
            endpoint: The specific API endpoint (e.g., 'record', 'classify').
        """
        url = target_address.get_url(endpoint)
        try:
            # Using requests.post as implied by the REST context in the labs
            print(f"[JsonIO] Sending data to {url}...")
            response = requests.post(url, json=data)
            return response.status_code in [200, 201]
        except requests.RequestException as e:
            print(f"[JsonIO] Error sending to {url}: {e}")
            return False

    def receive(self) -> Optional[Dict[str, Any]]:
        """
        Placeholder for receiving data.
        In the Flask architecture, reception is handled by the Controller
        triggered by the API route, not actively by this class.
        """
        return None