import React from 'react';
import { Card, Typography, Input, Row, Col, Space } from 'antd';
import {
  QuestionCircleOutlined,
  BookOutlined,
  LaptopOutlined,
  SafetyOutlined,
  SettingOutlined,
  TeamOutlined,
} from '@ant-design/icons';

const { Title, Text } = Typography;
const { Search } = Input;

const kbCategories = [
  {
    title: 'Getting Started',
    description: 'New employee guides and onboarding',
    icon: <QuestionCircleOutlined style={{ fontSize: 28, color: '#667eea' }} />,
    articles: 12,
  },
  {
    title: 'Hardware & Devices',
    description: 'Setup guides for laptops, printers, phones',
    icon: <LaptopOutlined style={{ fontSize: 28, color: '#764ba2' }} />,
    articles: 8,
  },
  {
    title: 'Security & Passwords',
    description: 'Password resets, MFA, security policies',
    icon: <SafetyOutlined style={{ fontSize: 28, color: '#ff4d4f' }} />,
    articles: 15,
  },
  {
    title: 'Software & Tools',
    description: 'How to use common business software',
    icon: <SettingOutlined style={{ fontSize: 28, color: '#52c41a' }} />,
    articles: 20,
  },
  {
    title: 'Network & Connectivity',
    description: 'VPN, WiFi, remote access troubleshooting',
    icon: <BookOutlined style={{ fontSize: 28, color: '#faad14' }} />,
    articles: 6,
  },
  {
    title: 'Policies & Procedures',
    description: 'IT policies, acceptable use, GDPR',
    icon: <TeamOutlined style={{ fontSize: 28, color: '#13c2c2' }} />,
    articles: 10,
  },
];

const PortalKnowledge: React.FC = () => {
  return (
    <div>
      <Title level={4} style={{ marginBottom: 4 }}>Knowledge Base</Title>
      <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
        Find answers to common questions and helpful guides.
      </Text>

      <Search
        placeholder="Search articles..."
        size="large"
        style={{ maxWidth: 500, marginBottom: 32 }}
        enterButton
      />

      <Row gutter={[16, 16]}>
        {kbCategories.map((cat) => (
          <Col xs={24} sm={12} md={8} key={cat.title}>
            <Card hoverable style={{ height: '100%' }}>
              <Space align="start">
                <div style={{ paddingTop: 2 }}>{cat.icon}</div>
                <div>
                  <Text strong style={{ display: 'block', marginBottom: 4 }}>{cat.title}</Text>
                  <Text type="secondary" style={{ fontSize: 13 }}>{cat.description}</Text>
                  <br />
                  <Text type="secondary" style={{ fontSize: 12, marginTop: 8, display: 'inline-block' }}>
                    {cat.articles} articles
                  </Text>
                </div>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
};

export default PortalKnowledge;
