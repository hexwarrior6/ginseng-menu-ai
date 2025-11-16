# Menu.ai 前端架构设计

## 技术栈选择
- React 18 (核心框架)
- React Router v6 (路由管理)
- Axios (HTTP客户端)
- TailwindCSS (样式框架)
- React Query (数据获取和缓存)
- Zustand (状态管理)
- React Hook Form (表单处理)

## 应用结构
```
src/
├── assets/           # 静态资源
├── components/       # 可复用组件
├── layouts/          # 页面布局组件
├── pages/            # 页面组件
├── services/         # API服务层
├── stores/           # 状态管理
├── hooks/            # 自定义Hooks
├── utils/            # 工具函数
├── App.jsx           # 根组件
└── main.jsx          # 应用入口
```

## 主要功能模块

### 1. 菜品展示模块
- 菜品列表页 (DishListPage)
- 菜品详情页 (DishDetailPage)
- 菜品分类筛选
- 搜索功能

### 2. 推荐系统模块
- 访客推荐页 (GuestRecommendationPage)
- 用户推荐页 (UserRecommendationPage)
- 个性化设置面板

### 3. 菜品管理模块 (管理员)
- 添加菜品 (AddDishForm)
- 编辑菜品 (EditDishForm)
- 菜品上下架管理
- 菜品数据分析

### 4. 用户系统模块
- 用户偏好设置
- 饮食限制管理
- 收藏夹功能

## 核心组件设计

### 公共组件
- Header (导航栏)
- Footer (页脚)
- DishCard (菜品卡片)
- RecommendationCard (推荐卡片)
- CategoryFilter (分类筛选器)
- SearchBar (搜索框)
- LoadingSpinner (加载指示器)
- ErrorMessage (错误提示)

### 页面组件
- HomePage (首页)
- MenuPage (菜单页)
- RecommendationPage (推荐页)
- DishManagementPage (菜品管理页)
- UserProfilePage (用户资料页)

## API服务层设计
- dishService (菜品相关API)
- recommendationService (推荐相关API)
- userService (用户相关API)

## 状态管理设计
使用Zustand管理全局状态：
- 用户状态 (认证、偏好设置)
- 菜品数据缓存
- 推荐结果缓存
- UI状态 (加载、错误等)

## 响应式设计
- 移动优先设计原则
- 断点设置：sm(640px), md(768px), lg(1024px), xl(1280px)
- 触摸友好的交互设计