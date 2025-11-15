import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import json
from flask import Flask

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入应用
from app import app
from database import init_db, get_db, close_db

class MenuAITestCase(unittest.TestCase):
    
    def setUp(self):
        """测试前的设置"""
        # 配置测试应用
        app.config['TESTING'] = True
        app.config['DATABASE_URL'] = 'mongodb://localhost:27017/menu_ai_test'  # 使用测试数据库
        
        self.client = app.test_client()
        
        # 初始化测试数据库
        with app.app_context():
            init_db(app)
    
    def tearDown(self):
        """测试后的清理"""
        # 关闭数据库连接
        close_db()
    
    def test_home_page(self):
        """测试首页接口"""
        response = self.client.get('/')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', data)
        self.assertEqual(data['message'], 'Menu.ai Backend Service is running!')
    
    def test_mock_recommendations(self):
        """测试模拟推荐接口"""
        response = self.client.get('/api/recommendations/test/mock')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('recommendations', data)
        self.assertGreaterEqual(len(data['recommendations']), 1)
    
    @patch('services.dish_service.DishService.add_dish')
    def test_add_dish(self, mock_add_dish):
        """测试添加菜品接口（模拟服务层）"""
        # 配置模拟返回值
        mock_dish = MagicMock()
        mock_dish.dish_id = 'test_dish_id'
        mock_add_dish.return_value = mock_dish
        
        # 准备测试数据
        dish_data = {
            "name": "测试菜品",
            "description": "这是一道测试菜品",
            "category": "测试类别"
        }
        
        # 发送POST请求
        response = self.client.post('/api/dishes', 
                                    data=json.dumps(dish_data),
                                    content_type='application/json')
        
        # 验证响应
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', data)
        self.assertEqual(data['message'], '菜品添加成功')
        self.assertIn('dish_id', data)
        
        # 验证服务方法是否被调用
        mock_add_dish.assert_called_once()

if __name__ == '__main__':
    unittest.main()