from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

@dataclass
class ComfyImageMeta:
    filename: str
    subfolder: str
    type: str
    format: str = ".png"  # 默认值根据实际API调整
    node_id: Optional[str] = None  # 关联的节点ID

@dataclass
class WorkflowStatus:
    prompt_id: str
    completed: bool
    status_str: str
    images_meta: List[ComfyImageMeta]
    messages: List[Dict[str, Any]] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None


@dataclass
class ComfyConfig:
    host: str
    port: int
    upload_dir: str
    base_url: str = None

    def __post_init__(self):
        self.base_url = f"http://{self.host}:{self.port}"