import { useEffect, useState } from 'react';
import { getServices } from './api/service.js';
import ServiceCard from './components/ServiceCard';
import './App.css';

function App() {
  const [services, setServices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchServices = async () => {
      try {
        const data = await getServices();
        setServices(data);
        setLoading(false);
      } catch (error) {
        setError('无法加载服务列表，请检查后端是否运行');
        setLoading(false);
        console.error('加载服务失败:', error);
      }
    };
    fetchServices();
  }, []);

  return (
    <div className="app-container">
      <h1>ComfyBox 服务测试平台</h1>
      {loading && <p>加载中...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <div className="service-grid">
        {services.map((service, index) => (
          <ServiceCard key={index} service={service} />
        ))}
      </div>
    </div>
  );
}

export default App;