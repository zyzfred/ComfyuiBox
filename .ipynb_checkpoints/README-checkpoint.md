comfyui-api/
├── app/
│   ├── __init__.py
│   ├── main.py          # 主入口和路由定义
│   ├── schemas.py       # 请求/响应模型定义
│   ├── services/        # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── comfyui_service.py  # ComfyUI 工作流交互逻辑
│   │   └── image_processor.py  # 图片处理逻辑
│   ├── utils/           # 工具函数
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── workers/         # 异步任务（预留并发模块）
│       └── __init__.py
├── config/              # 配置文件
│   └── settings.py
├── tests/               # 测试用例
│   ├── __init__.py
│   └── test_api.py
├── requirements.txt
├── workplace.ipynb      # 开发笔记
└── README.md