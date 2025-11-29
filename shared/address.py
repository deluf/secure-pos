class Address:
    """
    Value Object representing a network address (IP and Port).
    """

    def __init__(self, ip_addr: str, port: int):
        self.ip_addr = ip_addr
        self.port = port

    def get_url(self, endpoint: str = "") -> str:
        """Helper to construct a full URL for Flask/Requests."""
        base = f"http://{self.ip_addr}:{self.port}"
        if endpoint:
            return f"{base}/{endpoint}"
        return base

    def __str__(self):
        return f"{self.ip_addr}:{self.port}"