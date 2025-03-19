import json
from pathlib import Path
from .types import ComfyConfig


def load_comfy_config(server_name: str) -> ComfyConfig:
    """根据服务器名称加载配置"""
    servers_config = json.loads(Path("comfy_servers.json").read_text())
    server = next((s for s in servers_config["servers"] if s["name"] == server_name), None)
    if not server:
        raise ValueError(f"未找到服务器配置: {server_name}")
    
    return ComfyConfig(
        host=server["host"],
        port=server["port"],
        upload_dir=server["upload_dir"]
    )