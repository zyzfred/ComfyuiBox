import axios from 'axios';

// 定义基础 API URL
const API_URL = 'http://10.5.101.151:8686' || import.meta.env.VITE_API_URL;

// 获取所有服务列表
export const getServices = async () => {
  try {
    const response = await axios.get(`${API_URL}/services`);
    return response.data;
  } catch (error) {
    console.log(`获取服务url: ${API_URL}/services`)
    console.error('获取服务列表失败:', error);
    throw error;
  }
};

// 调用服务执行接口
export const executeService = async (serviceName, payload) => {
  try {
    const response = await await axios.post(
      `${API_URL}/service/${serviceName}/execute`,
      payload,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.log(`请求携带payload: ${payload}`)
    console.error(`调用服务 ${serviceName} 失败:`, error);
    throw error;
  }
};