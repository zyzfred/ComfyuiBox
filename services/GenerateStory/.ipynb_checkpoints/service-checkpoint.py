from common.base_service.service import BaseService

class GenerateStoryService(BaseService):
    def __init__(self):
        super().__init__("GenerateStory")  # 必须调用基类初始化
        
        # 如果需要自定义路由
        @self.router.get("/custom")  # 自动继承 /service/{name} 前缀
        def custom_endpoint():
            return {"message": "自定义接口"}