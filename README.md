comfybox/
├── services/               # 所有工作流服务根目录
│   ├── __init__.py
│   ├── base_service/       # 服务基类模板（抽象核心逻辑）
│   │   ├── __init__.py
│   │   ├── service.py      # 服务基类（接口规范）
│   │   └── workflow_runner.py  # 工作流执行核心逻辑
│   └── multi_angle/        # 示例工作流服务（多角度生成）
│       ├── __init__.py
│       ├── workflow.json   # 工作流定义文件（ComfyUI格式）
│       ├── config.json     # 工作流配置文件（输入映射）
│       ├── api/            # 对外暴露的接口实现
│       │   ├── __init__.py
│       │   └── endpoints.py  # 该工作流的专属API
│       ├── Dockerfile      # 容器化配置
│       └── requirements.txt 
├── common/                 # 公共模块
│   ├── comfy_adapter/      # ComfyUI 适配器
│   │   ├── executor.py     # 工作流执行器
│   │   └── types.py        # ComfyUI 类型定义
│   └── utils/              # 工具函数
│       ├── file_handler.py # 文件路径处理
│       └── validators.py   # 输入校验工具
├── frontend/               # 前端代码（独立微服务）
│   ├── public/
│   └── src/
│       ├── services/       # 前端服务发现模块
│       └── components/     # 工作流展示组件
├── configs/                # 全局配置
│   ├── env.template        # 环境变量模板
│   └── service_registry.json # 服务注册表（可选）
├── scripts/                # 部署脚本
│   ├── deploy_service.sh   # 服务部署脚本
│   └── generate_config.py  # 配置生成工具
└── docker-compose.yml      # 服务编排文件