import os
import json
import gradio as gr
import requests
from dotenv import load_dotenv
from common.utils.file_handler import get_service_names, get_service_config
from pathlib import Path

load_dotenv()
WEBUI_PORT = int(os.getenv("WEBUI_PORT", 8688))
BASE_API_URL = f"http://{os.getenv('API_HOST', 'localhost')}:{os.getenv('API_PORT', 8686)}"
INPUT_DIR = Path(os.getenv("INPUT_DIR"))

def load_services():
    return [
        {
            "name": name,
            "api_url": f"{BASE_API_URL}/service/{name}/execute",
            "input_mappings": get_service_config(name).get("input_mappings", [])
        }
        for name in get_service_names()
    ]

def execute_service(service_info, *args):
    payload = {}
    for i, mapping in enumerate(service_info['input_mappings']):
        key = mapping['input_field']
        value = args[i]
        
        if mapping['data_type'] == 'filepath':
            # 正确处理 Gradio 文件对象
            if isinstance(value, dict) and 'orig_name' in value:
                # 获取原始文件名（非临时路径）
                filename = value['orig_name']
                
                # 构建合法路径
                valid_path = Path(os.getenv("INPUT_DIR")) / filename
                
                # 移动文件到输入目录（如果需要）
                if not valid_path.exists():
                    shutil.copy(value['name'], valid_path)
                
                # 使用相对路径（与 curl 命令一致）
                payload[key] = str(valid_path.relative_to(
                    Path(os.getenv("INPUT_DIR")).parent
                ))
            else:
                raise gr.Error("文件上传格式错误")
        else:
            payload[key] = value
    
    try:

        for k, v in payload.items():
            if v[0] == "\"" and v[-1] == "\"":
                payload[k] = v[1:-1]
        print("发送的 Payload:", payload)

        response = requests.post(
            service_info['api_url'],
            json=payload,
            timeout=300
        )
        result = response.json()
        
        print("原始响应:", result)  # 查看原始响应结构
        
        if result['status'] == 'completed':
            return [
                os.path.join(
                    os.getenv("OUTPUT_DIR"),
                    Path(img).name
                ) for img in result['images']
            ]
            
        return ["执行失败，请检查服务日志"]
    
    except Exception as e:
        print("错误详情:", str(e))  # 输出完整错误信息
        return [f"错误：{str(e)}"]

# 构建界面
SERVICES = load_services()

with gr.Blocks(css=".service-card {border: 1px solid #ddd; padding: 20px; margin: 10px}") as demo:
    gr.Markdown("# ComfyBox 服务测试平台")
    
    for i in range(0, len(SERVICES), 3):
        with gr.Row():
            for service in SERVICES[i:i+3]:
                with gr.Column():
                    gr.Markdown(f"### {service['name']}")
                    
                    inputs = []
                    for mapping in service['input_mappings']:
                        if mapping['data_type'] == 'filepath':
                            inputs.append(gr.File(
                                label=mapping['input_field'],
                                file_types=["image"],
                                file_count="single"
                            ))
                        elif mapping['data_type'] in ['int', 'float']:
                            inputs.append(gr.Number(
                                label=mapping['input_field'],
                                value=mapping.get('default_value')
                            ))
                        else:
                            inputs.append(gr.Textbox(
                                label=mapping['input_field'],
                                value=mapping.get('default_value', '')
                            ))
                    
                    output = gr.Gallery(
                        label="输出结果",
                        columns=2,
                        height=400,
                        object_fit="contain"  # 确保图片正确缩放
                    )
                    
                    execute_btn = gr.Button("立即生成")
                    
                    execute_btn.click(
                        fn=execute_service,
                        inputs=[gr.JSON(value=service)] + inputs,
                        outputs=output
                    )

if __name__ == "__main__":
    demo.launch(
        server_name=os.getenv("WEBUI_HOST", "0.0.0.0"),
        server_port=WEBUI_PORT,
        share=False
    )