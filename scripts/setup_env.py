import os
import json
from pathlib import Path

def setup_environment():
    """生成环境变量文件"""
    project_root = Path(__file__).parent.parent.resolve()
    
    # 生成路径配置
    env_data = {
        "PROJECT_ROOT": str(project_root),
        "SERVICE_ROOT": str(project_root / "services"),
        "SERVICE_CONFIG": str(project_root / "services_config.json"),
        "WORKFLOW_DIR": str(project_root / "data/workflows"),
        "INPUT_DIR": str(project_root / "data/inputs"),
        "OUTPUT_DIR": str(project_root / "data/outputs"),
        "API_HOST": "0.0.0.0",
        "API_PORT": "8686",
        "WEBUI_HOST": "0.0.0.0",
        "WEBUI_PORT": "8688",
        "VITE_API_URL": "http://0.0.0.0:8688",
        "COMFY_CONFIG": str(project_root / "comfy_servers.json")
    }
    
    # 写入 .env 文件
    with open(project_root / ".env", "w") as f:
        for key, value in env_data.items():
            f.write(f"{key}={value}\n")
            print(f"已生成环境变量 {key}: {value}")
    
    print(f"环境变量已生成在: {project_root / '.env'}")

if __name__ == "__main__":
    setup_environment()
