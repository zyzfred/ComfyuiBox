import os
import json
import shutil
import argparse
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

load_dotenv()
env = Environment(loader=FileSystemLoader(os.path.join(os.getcwd(), 'templates')))
service_root = os.getenv("SERVICE_ROOT")

def parse_arguments():
    parser = argparse.ArgumentParser(description='ComfyBox 服务生成工具')
    parser.add_argument(
        '-c', '--config',
        type=str,
        default=os.getenv("SERVICE_CONFIG"),
        help='服务配置文件路径（默认: services_config.json）'
    )
    return parser.parse_args()

def generate_services(config_file: str):
    print(f"正在使用配置文件: {os.path.abspath(config_file)}")
    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"配置文件不存在: {config_file}")
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    print(f"\n=== 开始生成 {len(config.get('services', []))} 个服务 ===")
    
    for idx, service in enumerate(config.get('services', []), 1):
        print(f"\n[{idx}/{len(config['services'])}] ", end="")
        generate_single_service(service)

def generate_single_service(service_config: dict):
    required_fields = ['name', 'server', 'workflow', 'config']
    if any(field not in service_config for field in required_fields):
        raise ValueError(f"服务配置缺失必要字段: {required_fields}")
    
    service_name = service_config['name']
    server_name = service_config['server']
    service_dir = os.path.join(service_root, service_name)
    
    print(f"开始生成服务: {service_name}")
    print(f"  关联服务器: {server_name}")
    print(f"  Workflow路径: {service_config['workflow']}")
    print(f"  Config路径: {service_config['config']}")
    
    os.makedirs(service_dir, exist_ok=True)
    
    try:
        print("  正在复制工作流文件...", end="")
        shutil.copy(
            service_config['workflow'],
            os.path.join(service_dir, 'workflow.json')
        )
        print("完成")
        
        print("  正在复制配置文件...", end="")
        shutil.copy(
            service_config['config'],
            os.path.join(service_dir, 'config.json')
        )
        print("完成")
    except Exception as e:
        print(f"\n  [失败] 文件操作失败: {str(e)}")
        raise
    
    try:
        print("  正在生成服务类...", end="")
        template = env.get_template('service_template.py')
        content = template.render(
            service_name=service_name,
            server_name=server_name,  # 新增：传递服务器名称
            input_mappings=parse_config(service_config['config'])
        )
        
        with open(os.path.join(service_dir, 'service.py'), 'w') as f:
            f.write(content)
        print("完成")
    except Exception as e:
        print(f"\n  [失败] 服务类生成失败: {str(e)}")
        raise

def parse_config(config_path: str) -> list:
    try:
        with open(config_path, 'r') as f:
            return json.load(f).get('input_mappings', [])
    except Exception as e:
        raise ValueError(f"配置解析失败: {str(e)}")

if __name__ == '__main__':
    args = parse_arguments()
    try:
        generate_services(args.config)
        print("\n=== 所有服务生成完毕！===")
    except Exception as e:
        print(f"\n=== 生成终止: {str(e)} ===")
        exit(1)