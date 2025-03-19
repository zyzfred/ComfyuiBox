import os
import json
import argparse
import shutil
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# 默认配置文件路径
COMFY_SERVERS_PATH = os.getenv("COMFY_CONFIG", "../comfy_servers.json")
SERVICES_CONFIG_PATH = os.getenv("SERVICE_CONFIG", "../services_config.json")

def load_json(file_path: str) -> dict:
    """加载 JSON 文件"""
    if not Path(file_path).exists():
        raise FileNotFoundError(f"配置文件不存在: {file_path}")
    with open(file_path, 'r') as f:
        return json.load(f)

def write_json(file_path: str, data: dict):
    """写入 JSON 文件"""
    with open(file_path, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def validate_workflow_directory(workflow_dir: str) -> bool:
    """验证工作流目录是否存在以及必要文件是否完整"""
    workflow_dir = Path(workflow_dir)
    if not workflow_dir.exists():
        raise FileNotFoundError(f"工作流目录不存在: {workflow_dir}")
    
    required_files = ["workflow.json", "config.json"]
    for file in required_files:
        if not (workflow_dir / file).exists():
            raise FileNotFoundError(f"缺少必要文件: {workflow_dir / file}")
    
    return True

def generate_service_name_from_path(workflow_dir: str) -> str:
    """根据工作流路径生成默认服务名称"""
    dir_name = Path(workflow_dir).name
    items = dir_name.split("_")
    return "".join(item.capitalize() for item in items)

def append_or_rewrite_services(
    services_config: list,
    new_services: list,
    mode: str = "append"
) -> list:
    """追加或重写服务配置"""
    if mode == "rewrite":
        return new_services
    
    existing_names = {service["name"] for service in services_config}
    for service in new_services:
        if service["name"] not in existing_names:
            services_config.append(service)
    
    return services_config

def backup_file(file_path: str):
    """备份文件"""
    backup_path = f"{file_path}.bak"
    if Path(file_path).exists():
        shutil.copy(file_path, backup_path)
        print(f"已备份原文件到: {backup_path}")

def process_server_directory(server_dir: Path, server_name: str) -> list:
    """处理服务器目录下的所有工作流"""
    new_services = []
    for workflow_dir in server_dir.iterdir():
        new_service = process_workflow_directory(workflow_dir, server_name)
        new_services += new_service
        
    return new_services

def process_workflow_directory(workflow_dir: Path, server_name: str, service_name: str = None) -> list:
    """处理单个工作流目录"""
    try:
        # 验证工作流目录
        validate_workflow_directory(workflow_dir)
        
        # 生成服务名称
        service_name = service_name or generate_service_name_from_path(workflow_dir)
        
        # 构造新服务配置
        new_service = {
            "name": service_name,
            "server": server_name,
            "workflow": str(workflow_dir / "workflow.json"),
            "config": str(workflow_dir / "config.json"),
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        print(f"成功生成服务配置: {service_name}")
        return [new_service]
    except Exception as e:
        print(f"处理失败: {str(e)}")
        return []
        
def main():
    # 参数解析
    parser = argparse.ArgumentParser(description="ComfyBox 服务配置生成工具")
    parser.add_argument(
        "-s", "--server",
        type=str,
        required=True,
        help="服务器名称（必须）"
    )
    parser.add_argument(
        "-d", "--directory",
        type=str,
        required=True,
        help="服务器目录或工作流目录（必须）"
    )
    parser.add_argument(
        "-n", "--service_name",
        type=str,
        default=None,
        help="服务名称（非必须，默认为目录名）"
    )
    parser.add_argument(
        "-m", "--mode",
        type=str,
        choices=["append", "rewrite"],
        default="append",
        help="模式：追加或重写（默认追加）"
    )
    args = parser.parse_args()

    # 加载现有配置
    try:
        comfy_servers = load_json(COMFY_SERVERS_PATH)
        servers = comfy_servers.get("servers", [])
        server = next((s for s in servers if s["name"] == args.server), None)
        if not server:
            raise ValueError(f"未找到服务器配置: {args.server}")
        
        directory = Path(args.directory)
        if not directory.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")
        
        # 判断是服务器目录还是工作流目录
        new_services = []
        if directory.is_dir() and any(subdir.is_dir() for subdir in directory.iterdir()):
            # 服务器目录
            print("检测到服务器目录，批量处理工作流...")
            new_services = process_server_directory(directory, args.server)
        else:
            # 工作流目录
            print("检测到工作流目录，单独处理...")
            new_services = process_workflow_directory(directory, args.server, args.service_name)
        
        if not new_services:
            print("未生成任何新的服务配置")
            return
        
        # 加载现有服务配置
        if Path(SERVICES_CONFIG_PATH).exists():
            services_config = load_json(SERVICES_CONFIG_PATH)
        else:
            services_config = {"services": []}

        # 追加或重写模式
        services_config["services"] = append_or_rewrite_services(
            services_config["services"],
            new_services,
            mode=args.mode
        )
        
        # 备份原文件（仅在重写模式下）
        if args.mode == "rewrite":
            backup_file(SERVICES_CONFIG_PATH)
        
        # 写入新的服务配置
        write_json(SERVICES_CONFIG_PATH, services_config)
        print("=== 成功更新服务配置 ===")
    except Exception as e:
        print(f"=== 错误: {str(e)} ===")
        exit(1)

if __name__ == "__main__":
    main()