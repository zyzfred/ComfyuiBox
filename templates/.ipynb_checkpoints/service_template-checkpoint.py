from common.base_service.service import BaseService

class {{ service_name }}Service(BaseService):
    def __init__(self):
        super().__init__(
            service_name="{{ service_name }}",
            server_name="{{ server_name }}",  # 新增服务器名称参数
        )
        
        # 如果需要自定义路由
        @self.router.get("/custom")
        def custom_endpoint():
            return {"message": "自定义接口"}