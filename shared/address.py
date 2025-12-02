"""
A module defining the Address class representing a network address (IP and Port)
"""

class Address:
    """
    Object representing a network address (IP and Port)
    """

    def __init__(self, ip: str, port: int):
        self.ip = ip
        self.port = port
        print(f"created {self.ip}:{self.port}")

    def __str__(self):
        return f"{self.ip}:{self.port}"
