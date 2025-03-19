import os
import requests
import json
import base64
from dotenv import load_dotenv
from typing import Dict, List, Union
from pathlib import Path
from .types import ComfyConfig, WorkflowStatus, ComfyImageMeta
from requests.exceptions import RequestException
load_dotenv()

class ComfyExecutor:
    def __init__(self, config: ComfyConfig):
        self.config = config
        self.base_url = f"http://{config.host}:{config.port}"
        self.upload_dir = config.upload_dir
        

    def submit_workflow(self, workflow: Dict) -> str:
        """提交工作流并返回 prompt_id"""
        try:
            url = f"{self.base_url}/prompt"
            response = requests.post(
                url,
                json=workflow,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "prompt_id" in data:
                    return data["prompt_id"]
                raise ValueError("Invalid response format")
            
            # 处理非200响应
            error_msg = f"HTTP {response.status_code}: {response.text}"
            raise RequestException(error_msg)
            
        except Exception as e:
            raise RuntimeError(f"提交失败: {str(e)}")

    def get_workflow_status(self, prompt_id: str) -> WorkflowStatus:
        """增强版工作流状态查询"""
        try:
            url = f"{self.base_url}/history/{prompt_id}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # 触发HTTP错误
            
            history_data = response.json().get(prompt_id, {})
            outputs = history_data.get("outputs", {})
            status_info = history_data.get("status", {})
            
            # 提取图片元数据（支持多节点输出）
            images_meta = []
            for node_id, node_data in outputs.items():
                if "images" not in node_data:
                    continue
                for img in node_data["images"]:
                    images_meta.append(ComfyImageMeta(
                        filename=img["filename"],
                        subfolder=img.get("subfolder", ""),
                        type=img["type"],
                        node_id=node_id
                    ))
            
            return WorkflowStatus(
                prompt_id=prompt_id,
                completed=status_info.get("completed", False),
                status_str=status_info.get("status_str", "unknown"),
                images_meta=images_meta,
                messages=history_data.get("status", {}).get("messages", []),
                meta=history_data.get("meta", {})
            )
            
        except requests.exceptions.RequestException as e:
            return WorkflowStatus(
                prompt_id=prompt_id,
                completed=False,
                status_str="error",
                images_meta=[],
                error=str(e)
            )

    def download_images(
        self, 
        images_meta: List[ComfyImageMeta],
        output_dir: str = os.getenv("OUTPUT_DIR", "./outputs")
    ) -> Dict[str, str]:  # 返回 Base64 字符串
        """下载并编码图片为 Base64"""
        results = {}
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        for meta in images_meta:
            try:
                params = {
                    "filename": meta.filename,
                    "type": meta.type,
                    "subfolder": meta.subfolder,
                    "format": meta.format
                }
                response = requests.get(
                    f"{self.base_url}/view",
                    params=params,
                    timeout=10
                )
                response.raise_for_status()
                
                # 转换为 Base64
                encoded_image = base64.b64encode(response.content).decode('utf-8')
                results[meta.filename] = f"data:image/png;base64,{encoded_image}"
                
                # 保存文件（可选）
                filepath = Path(output_dir) / meta.filename
                with open(filepath, "wb") as f:
                    f.write(response.content)
                
            except Exception as e:
                results[meta.filename] = None
                print(f"下载失败 [{meta.filename}]: {str(e)}")
        
        return results