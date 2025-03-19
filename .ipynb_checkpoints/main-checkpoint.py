# main.py
import os
import sys
import importlib
import uvicorn
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.routing import APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from common.utils.file_handler import get_service_names, get_service_config
from dotenv import load_dotenv
load_dotenv()

# 添加项目根目录到 Python 路径
ROOT_DIR = Path(os.getenv("PROJECT_ROOT")).resolve()
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR")).resolve()
sys.path.append(str(ROOT_DIR))

# 创建主应用
app = FastAPI()

# 在主程序中添加服务列表接口
@app.get("/services")
def list_services():
    return [
        {
            "name": name,
            "input_parameters": get_service_config(name).get("input_mappings", [])
        }
        for name in get_service_names()
    ]

@app.get("/routes")
async def list_routes():
    return {route.path: route.name for route in app.routes}

@app.on_event("startup")
async def debug_routes():
    print("\n=== 已注册路由 ===")
    for route in app.routes:
        if hasattr(route, "path"):
            print(f"{route.path} -> {route.name}")
    print("=================\n")

# 动态加载所有服务
def load_all_services():

    services_root = Path(os.getenv("SERVICE_ROOT"))
    for service_dir in services_root.iterdir():
        # 跳过隐藏目录
        if service_dir.name.startswith(("_", ".")):
            continue

        print(f"正在加载服务目录: {service_dir}")
        if not service_dir.is_dir():
            continue
            
        # 验证服务完整性
        service_file = service_dir / "service.py"
        if not service_file.exists():
            print(f"⚠️ 服务 {service_name} 缺少 service.py")
            continue

        service_name = service_dir.name
        if not (service_dir / "workflow.json").exists():
            print(f"⚠️ 服务目录 {service_name} 缺少 workflow.json")
            continue

        print(f"  正在挂载服务: {service_name}")
    
        try:
            # 动态导入服务模块
            spec = importlib.util.spec_from_file_location(
                f"services.{service_name}.service",
                service_file
            )
            service_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(service_module)
            
            # 创建服务实例
            service_class = getattr(service_module, f"{service_name}Service")
            service_instance = service_class()
            
            # 修正挂载方式（使用 include_router 而非 mount）
            app.include_router(
                service_instance.router,
                prefix=f"/service/{service_name}",  # 主程序统一添加前缀
                tags=[service_name]
            )
            
            print(f"✅ 服务 {service_name} 已挂载到 /service/{service_name}")
            print(f"  已注册路由: {[route.path for route in service_instance.router.routes]}")

            
        except Exception as e:
            print(f"❌ 加载服务 {service_name} 失败: {str(e)}")

# 自动加载所有服务
load_all_services()
print(f"\n=== 主程序路由表 ===")
print({route.path: route.name for route in app.routes})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（生产环境应限制具体域名）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 挂载前端静态文件
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")

# 返回前端 index.html
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    index_file = Path("frontend/dist/index.html")
    if not index_file.exists():
        return {"error": "Frontend files not found. Please build the frontend first."}
    return index_file.read_text()

# 挂载输出目录
app.mount(
    f"{str(OUTPUT_DIR)}",
    StaticFiles(directory=os.getenv("OUTPUT_DIR")),
    name="outputs"
)

if __name__ == "__main__":

    # 修复启动方式（使用模块路径启动）
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8686)),
        reload=True
    )


