import { useState } from 'react';
import { executeService } from '../api/service.js';
import ImageViewer from './ImageViewer';

const ServiceCard = ({ service }) => {
  console.log("渲染服务卡片:", service); // 调试输出
  const [output, setOutput] = useState([]);
  const [inputs, setInputs] = useState({});

  const handleInputChange = (nodeId, value) => {
    setInputs((prev) => ({ ...prev, [nodeId]: value }));
  };

  const handleSubmit = async () => {
    try {
      console.log(`原始输入: ${inputs}`)
      // 生成符合后端要求的 JSON 列表
      const payloadList = service.input_parameters.map((param) => ({
        node_id: param.node_id,
        [param.input_field]: inputs[param.node_id] || param.default_value
      }));

      console.log(`Json化输入: ${JSON.stringify(payloadList)}`)
      const result = await executeService(service.name, JSON.stringify(payloadList));
        
      if (result.status === 'completed') {
        setOutput(result.images);
      } else {
        setOutput(['执行失败，请查看日志']);
      }
    } catch (error) {
      setOutput([`请求失败: ${error.message}`]);
    }
  };

  return (
    <div className="service-card">
      <h3>{service.name}</h3>
      {service.input_parameters.map((param, index) => (
        <div key={index}>
          {param.data_type === 'filepath' ? (
            <input
              type="file"
              placeholder={param.description}
              name={param.node_id}
              onChange={(e) => handleInputChange(param.node_id, e.target.files[0])}
            />
          ) : (
            <input
              type={param.type === 'number' ? 'number' : 'text'}
              placeholder={param.description}
              name={param.node_id}
              defaultValue={param.default_value || ''}
              onChange={(e) => handleInputChange(param.node_id, e.target.value)}
            />
          )}
        </div>
      ))}
      <button onClick={handleSubmit}>立即生成</button>
      <ImageViewer images={output} />
    </div>
  );
};

export default ServiceCard;