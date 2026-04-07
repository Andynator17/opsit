import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Typography, Row, Col, Empty } from 'antd';
import {
  LaptopOutlined,
  KeyOutlined,
  MailOutlined,
  PrinterOutlined,
  WifiOutlined,
  MobileOutlined,
} from '@ant-design/icons';

const { Title, Text } = Typography;

const serviceCategories = [
  {
    title: 'Hardware',
    description: 'Laptops, monitors, peripherals, and more',
    icon: <LaptopOutlined style={{ fontSize: 32, color: '#667eea' }} />,
  },
  {
    title: 'Software & Licenses',
    description: 'Software installations and license requests',
    icon: <KeyOutlined style={{ fontSize: 32, color: '#764ba2' }} />,
  },
  {
    title: 'Email & Communication',
    description: 'Email accounts, distribution lists, Teams',
    icon: <MailOutlined style={{ fontSize: 32, color: '#52c41a' }} />,
  },
  {
    title: 'Network & Access',
    description: 'VPN, WiFi, file shares, permissions',
    icon: <WifiOutlined style={{ fontSize: 32, color: '#faad14' }} />,
  },
  {
    title: 'Printing',
    description: 'Printer setup, toner requests',
    icon: <PrinterOutlined style={{ fontSize: 32, color: '#ff4d4f' }} />,
  },
  {
    title: 'Mobile Devices',
    description: 'Phones, tablets, MDM enrollment',
    icon: <MobileOutlined style={{ fontSize: 32, color: '#13c2c2' }} />,
  },
];

const PortalServices: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div>
      <Title level={4} style={{ marginBottom: 4 }}>Service Catalog</Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
        Browse available IT services and submit a request.
      </Text>

      <Row gutter={[16, 16]}>
        {serviceCategories.map((cat) => (
          <Col xs={24} sm={12} md={8} key={cat.title}>
            <Card
              hoverable
              onClick={() => navigate(`/portal/tickets/new?type=request`)}
              style={{ textAlign: 'center', height: '100%' }}
              bodyStyle={{ padding: '32px 16px' }}
            >
              <div style={{ marginBottom: 16 }}>{cat.icon}</div>
              <Text strong style={{ display: 'block', marginBottom: 4, fontSize: 15 }}>
                {cat.title}
              </Text>
              <Text type="secondary" style={{ fontSize: 13 }}>{cat.description}</Text>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
};

export default PortalServices;
