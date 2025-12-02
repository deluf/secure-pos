from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RawSession:
    """
    raw session DTO.
    """
    uuid: str
    timestamp: List[Optional[float]]
    amount: List[Optional[float]]
    source_ip: List[Optional[str]]
    dest_ip: List[Optional[str]]
    longitude: List[Optional[float]]
    latitude: List[Optional[float]]
    label: Optional[int] = None
