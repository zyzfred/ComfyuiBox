import os
import json
from fastapi import HTTPException
from typing import List, Dict, Any

def validate_inputs(inputs: List[Dict], mappings: List[Dict]) -> List[Dict]:
    """
    参数校验器：
    1. 检查必填字段
    2. 验证数据类型
    3. 检查文件路径存在性
    4. 应用默认值
    """
    validated_data = []
    
    for i, mapping in enumerate(mappings):

        input = inputs[i]
        node_id = mapping.get("node_id")
        data_type = mapping.get("data_type")
        field = mapping.get("input_field")
        required = mapping.get("required", False)
        default = mapping.get("default_value")

        # 必填检查
        if required and node_id != input.get("node_id"):
            raise HTTPException(
                status_code=400,
                detail=f"输入缺失节点ID或者无法与映射节点ID对齐: {node_id}"
            )

        if required and field not in input:
            raise HTTPException(
                status_code=400,
                detail=f"输入参数缺失: {field}"
            )
        
        # 获取值（优先用户输入，否则使用默认值）
        value = input.get(field, default)
        
        # 非必填且无默认值时跳过
        if value is None and not required:
            continue
        
        # 类型校验
        if data_type == "int":
            if not isinstance(value, int):
                try:
                    value = int(value)
                    inputs[field] = value  # 自动转换类型
                except:
                    raise HTTPException(
                        status_code=400,
                        detail=f"参数 {field} 需要整数类型"
                    )
        
        elif data_type == "float":
            if not isinstance(value, float):
                try:
                    value = float(value)
                    inputs[field] = value
                except:
                    raise HTTPException(
                        status_code=400,
                        detail=f"参数 {field} 需要浮点数类型"
                    )
        
        elif data_type == "bool":
            if not isinstance(value, bool):
                if str(value).lower() in ["true", "false"]:
                    value = str(value).lower() == "true"
                    inputs[field] = value
                else:
                    raise HTTPException(
                        status_code=400,
                        detail=f"参数 {field} 需要布尔类型"
                    )
        
        elif data_type == "filepath":
            if not os.path.exists(value):
                raise HTTPException(
                    status_code=400,
                    detail=f"文件路径不存在: {value}"
                )
        
        elif data_type == "str":
            if not isinstance(value, str):
                inputs[field] = str(value)
        
        else:
            # 自定义类型校验（可扩展）
            raise HTTPException(
                status_code=400,
                detail=f"未知数据类型: {data_type}"
            )
        
        # 更新输入值（可能经过类型转换）
        input[node_id] = value
        validated_data.append(input)
        

    return validated_data

def validate_file_path(value: str):
    """验证文件路径格式"""
    if not value.startswith(os.getenv("INPUT_DIR")):
        raise ValueError(f"路径必须以 {os.getenv('INPUT_DIR')} 开头")
    if not os.path.exists(value):
        raise FileNotFoundError(f"文件不存在: {value}")

def validate_base64_image(data: str):
    if not data.startswith("data:image"):
        raise ValueError("无效的 Base64 图片格式")
    if len(data.split(",")) != 2:
        raise ValueError("缺少 Base64 数据头")