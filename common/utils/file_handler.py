# common/utils/file_handler.py
import os
import json
from typing import Dict, List
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def get_service_names() -> List[str]:
    """获取所有服务名称"""
    services_dir = Path(os.getenv("SERVICE_ROOT"))
    return [
        d.name for d in services_dir.iterdir()
        if d.is_dir() and 
           not d.name.startswith("__") and
           (d / "service.py").exists()
    ]

def get_service_path(service_name: str) -> str:
    """获取服务的具体路径"""
    return Path(os.getenv("SERVICE_ROOT")) / service_name
    
def get_service_config(service_name: str) -> Dict:
    """获取服务配置"""
    config_path = get_service_path(service_name) / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件缺失: {config_path}")
    with open(config_path, 'r') as f:
        return json.load(f)
    

def get_project_root() -> Path:
    """获取项目根目录"""
    return Path(os.getenv("PROJECT_ROOT", Path.cwd()))

def get_service_config_path() -> Path:
    """获取服务配置文件路径"""
    return Path(os.getenv("SERVICE_CONFIG"))

def get_workflow_path(service_name: str) -> Path:
    """获取工作流目录路径"""
    return Path(os.getenv("WORKFLOW_DIR")) / service_name

def get_input_dir() -> Path:
    """获取输入目录"""
    return Path(os.getenv("INPUT_DIR"))

def get_output_dir() -> Path:
    """获取输出目录"""
    return Path(os.getenv("OUTPUT_DIR"))
