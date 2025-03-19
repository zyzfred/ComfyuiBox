以下是完整的 `README.md` 文档，详细描述了项目的使用方法和配置规范：

---

# ComfyUI Box 项目文档

ComfyUI Box 是一个基于 ComfyUI 的多服务器工作流管理工具。通过该工具，您可以轻松管理和生成多个 ComfyUI 服务，并动态扩展新的服务器和工作流。

---

## **1. 依赖安装**

### **1.1 前端依赖**
1. 进入前端目录：
   ```bash
   cd frontend
   ```
2. 安装依赖：
   ```bash
   npm install
   ```
3. 构建前端代码：
   ```bash
   npm run build
   ```

### **1.2 后端依赖**
1. 安装 Python 依赖（建议使用虚拟环境）：
   ```bash
   pip install -r requirements.txt
   ```

---

## **2. 配置文件说明**

### **2.1 `comfy_servers.json` 配置**
`comfy_servers.json` 文件用于定义所有 ComfyUI 服务器的配置信息。每个服务器必须包含以下字段：
- `name`: 服务器名称（唯一标识符）。
- `host`: 服务器的 IP 地址或域名。
- `port`: 服务器的端口号。
- `upload_dir`: 服务器的上传文件目录路径。

#### 示例配置：
```json
{
  "servers": [
    {
      "name": "server_a",
      "host": "10.5.101.152",
      "port": 8370,
      "upload_dir": "/data/ysp-comfyui-platforms/ComfyUI-G4/input"
    },
    {
      "name": "server_b",
      "host": "another-host",
      "port": 8371,
      "upload_dir": "/data/comfyui-b/inputs"
    }
  ]
}
```

#### 修改方法：
1. 打开 `comfy_servers.json` 文件。
2. 根据实际服务器信息添加或修改条目。
3. 确保每个服务器的 `name` 唯一。

---

## **3. 工作流目录规则**

### **3.1 目录结构**
- **一级目录**：`data/workflows/<server_name>`  
  - `<server_name>` 必须与 `comfy_servers.json` 中的服务器名称一致。
- **二级目录**：`<workflow_name>`  
  - 使用下划线 `_` 分隔单词，表示具体功能的工作流名称。例如：`generate_story`。

#### 示例结构：
```
data/
└── workflows/
    ├── server_a/
    │   ├── generate_story/
    │   │   ├── workflow.json
    │   │   └── config.json
    │   └── multi_angle/
    │       ├── workflow.json
    │       └── config.json
    └── server_b/
        └── future_service/
            ├── workflow.json
            └── config.json
```

---

## **4. `config.json` 配置**

### **4.1 配置规则**
`config.json` 文件用于定义工作流的输入参数映射关系。您需要根据 `workflow.json` 中的节点信息进行配置。

#### 配置字段说明：
- `workflow_name`: 工作流名称。
- `input_mappings`: 输入参数映射列表，每个映射包含以下字段：
  - `node_id`: 节点 ID。
  - `input_field`: 输入字段名称。
  - `data_type`: 数据类型（如 `str`, `int`, `filepath` 等）。
  - `required`: 是否必填。
  - `default_value`: 默认值（可选）。
  - `description`: 描述信息。

#### 示例配置：
```json
{
  "workflow_name": "generate_story",
  "input_mappings": [
    {
      "node_id": "5",
      "input_field": "prompt",
      "data_type": "str",
      "required": true,
      "default_value": "",
      "description": "输入主角的提示词"
    },
    {
      "node_id": "6",
      "input_field": "prompt",
      "data_type": "str",
      "required": true,
      "default_value": "",
      "description": "输入故事的第一张图片的提示词"
    }
  ]
}
```

---

## **5. 脚本使用说明**

### **5.1 初始化环境变量**
运行以下命令生成环境变量文件：
```bash
python scripts/setup_env.py
```

### **5.2 生成服务配置文件**
脚本路径：`scripts/generate_service_config.py`  
用途：为指定的服务器或工作流生成服务配置文件。

#### 参数说明：
- `-s, --server`: 服务器名称（必需）。
- `-d, --directory`: 目录路径（服务器目录或工作流目录，必需）。
- `-m, --mode`: 模式（`append` 或 `rewrite`，默认为 `append`）。
- `-n, --service_name`: 服务名称（非必需，仅在处理单个工作流时使用）。

#### 示例：
1. **重写模式**（清空原有配置并重新生成）：
   ```bash
   python scripts/generate_service_config.py -s server_a -d data/workflows/server_a -m rewrite
   ```
2. **追加模式**（保留原有配置并添加新服务）：
   ```bash
   python scripts/generate_service_config.py -s server_a -d data/workflows/server_a
   ```

### **5.3 生成服务代码**
脚本路径：`scripts/generate_service.py`  
用途：根据服务配置文件生成服务代码。

#### 参数说明：
- `-c, --config`: 服务配置文件路径（默认为 `services_config.json`）。

#### 示例：
```bash
python scripts/generate_service.py -c services_config.json
```

---

## **6. 启动程序**

运行以下命令启动主程序：
```bash
python main.py
```

---

## **7. 其他注意事项**

1. **工作流命名规范**：
   - 请确保工作流目录名称使用下划线分隔单词，并具有明确的功能描述。
2. **服务配置更新**：
   - 如果新增了服务器或工作流，请及时更新 `comfy_servers.json` 和 `services_config.json`。
3. **日志查看**：
   - 主程序运行时会输出日志信息，请关注终端输出以排查问题。

---

## **8. 联系方式**

如有任何问题，请联系项目维护者：
- Email: [your-email@example.com]
- GitHub: [your-github-profile]

---

希望这份文档能帮助您快速上手 ComfyUI Box！