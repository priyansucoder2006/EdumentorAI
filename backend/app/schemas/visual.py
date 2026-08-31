from typing import Dict, Any, Optional
from pydantic import BaseModel


class VisualDataSchema(BaseModel):
    type: str  # "math", "code", "diagram", "graph", "physics_sim", "biology_diagram", "timeline", "none"
    title: Optional[str] = None
    data: Dict[str, Any] = {}
    caption: Optional[str] = None
