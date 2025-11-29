from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class RawSession:
    """
    DTO representing an aggregated session.
    """
    uuid: str
    timestamp: List[Optional[float]] = field(default_factory=list)
    amount: List[Optional[float]] = field(default_factory=list)
    source_ip: List[Optional[str]] = field(default_factory=list)
    dest_ip: List[Optional[str]] = field(default_factory=list)
    longitude: List[Optional[float]] = field(default_factory=list)
    latitude: List[Optional[float]] = field(default_factory=list)
    label: Optional[int] = None