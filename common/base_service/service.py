import os
import json
import requests
import time
from abc import ABC
from typing import List, Dict, Any
from fastapi import Body, APIRouter, HTTPException
from fastapi.routing import APIRoute
from common.comfy_adapter.config_loader import load_comfy_config
from common.comfy_adapter.executor import ComfyExecutor
from common.utils.validators import validate_inputs
from common.utils.file_handler import get_service_path

class BaseService(ABC):
    def __init__(self, service_name: str, server_name: str):
        self.service_name = service_name
        self.server_name = server_name
        self.service_path = get_service_path(service_name)
        self.router = APIRouter()  # 改用 Router 而非独立 App
        
        # 加载工作流和配置文件
        self.workflow = self.load_workflow()
        self.config = self.load_config()
        self.comfy_config = load_comfy_config(self.server_name)
        self.comfy_executor = ComfyExecutor(self.comfy_config)
        
        # 注册路由
        self.register_routes()
        
    def load_workflow(self) -> Dict:
        """加载工作流文件"""
        workflow_path = os.path.join(self.service_path, "workflow.json")
        if not os.path.exists(workflow_path):
            raise FileNotFoundError(f"工作流文件缺失: {workflow_path}")
        with open(workflow_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_config(self) -> Dict:
        """加载服务配置"""
        config_path = os.path.join(self.service_path, "config.json")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件缺失: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def health_check(self) -> Dict[str, str]:
        """健康检查端点"""
        return {"status": "healthy", "service": self.service_name}

    def get_metadata(self) -> Dict[str, Any]:
        """获取服务元数据"""
        return {
            "service_name": self.service_name,
            "version": self.config.get("version", "1.0"),
            "input_parameters": [
                {
                    "name": m["input_field"],
                    "type": m["data_type"],
                    "description": m.get("description", "")
                }
                for m in self.config.get("input_mappings", [])
            ]
        }

    def register_routes(self):
        """显式注册标准路由"""
        self.router.add_api_route(
            "/execute",
            self.execute_workflow,
            methods=["POST"],
            tags=["Execution"]
        )
        self.router.add_api_route(
            "/health",
            self.health_check,
            methods=["GET"],
            tags=["Status"]
        )
        self.router.add_api_route(
            "/metadata",
            self.get_metadata,
            methods=["GET"],
            tags=["Info"]
        )
        
        # 允许子类扩展路由
        self.register_custom_routes()

    def register_custom_routes(self):
        """供子类实现自定义路由"""
        pass


    def execute_workflow(self, user_inputs: List[Dict]) -> Dict:
        """单次请求完成参数注入+执行"""
        print(f"原始输入: {user_inputs}")
        try:
            # 1. 参数校验
            validated_inputs = validate_inputs(
                user_inputs,
                self.config.get("input_mappings", [])
            )
            
            # 2. 深拷贝工作流
            modified_workflow = json.loads(json.dumps(self.workflow))
            
            # 3. 批量参数注入
            for i, mapping in enumerate(self.config.get("input_mappings", [])):
                node_id = mapping["node_id"]
                field = mapping["input_field"]
                input = validated_inputs[i]
                
                # 获取值（用户输入优先）
                value = input.get(field)
                
                if value is None:
                    # 使用工作流默认值
                    node = modified_workflow.get(node_id)
                    default_value = node.get("inputs", {}).get(field) if node else None
                    if default_value is None and mapping.get("required"):
                        raise HTTPException(400, f"节点{node_id}缺失必填参数{field}")
                else:
                    # 应用用户输入值
                    node = modified_workflow.get(node_id)
                    if node and "inputs" in node:
                        node["inputs"][field] = value

            # 4. 执行工作流
            modified_workflow = {"prompt": modified_workflow}
            prompt_id = self.comfy_executor.submit_workflow(modified_workflow)
            
            # 5. 轮询状态
            status = self.comfy_executor.get_workflow_status(prompt_id)
            while not status.completed:
                time.sleep(2)
                status = self.comfy_executor.get_workflow_status(prompt_id)
            
            # 6. 下载结果
            images = self.comfy_executor.download_images(status.images_meta)
            
            return {
                "status": "completed",
                "images": [
                    img_data for img_data in images.values() 
                    if img_data is not None
                ]
            }
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(500, f"执行失败: {str(e)}")
