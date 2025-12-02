<template>
  <div>
    <a-row :gutter="[16, 16]">
      <a-col :span="24">
        <h1>Dashboard</h1>
      </a-col>
    </a-row>

    <a-row :gutter="[16, 16]">
      <a-col :span="6">
        <a-card title="Total Users" class="stats-card">
          <template #extra>
            <a-tag color="blue">Users</a-tag>
          </template>
          <p style="font-size: 24px; font-weight: bold;">{{ stats.totalUsers }}</p>
          <p><a-icon type="user" /> Total registered users</p>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card title="Total Dishes Today" class="stats-card">
          <template #extra>
            <a-tag color="green">Dishes</a-tag>
          </template>
          <p style="font-size: 24px; font-weight: bold;">{{ stats.totalDishes }}</p>
          <p><a-icon type="appstore" /> Available dishes</p>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card title="Total Interactions" class="stats-card">
          <template #extra>
            <a-tag color="orange">Interactions</a-tag>
          </template>
          <p style="font-size: 24px; font-weight: bold;">{{ stats.totalInteractions }}</p>
          <p><a-icon type="interaction" /> User interactions</p>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card title="Daily Active Users" class="stats-card">
          <template #extra>
            <a-tag color="purple">Today</a-tag>
          </template>
          <p style="font-size: 24px; font-weight: bold;">{{ stats.dailyActiveUsers }}</p>
          <p><a-icon type="team" /> Active today</p>
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="[16, 16]" style="margin-top: 16px;" class="dashboard-row" type="flex">
      <a-col :span="8" class="dashboard-col">
        <a-card title="Recent Activity" class="full-height-card recent-activity-card">
          <a-list
            item-layout="horizontal"
            :data-source="recentActivity"
            :pagination="{
              pageSize: 4,
            }"
          >
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta>
                  <template #description>
                    <div>{{ getActionValue(item) }}</div>
                    <div class="activity-time">{{ new Date(item.timestamp).toLocaleString() }}</div>
                  </template>
                  <template #title>
                    <a>{{ getUserInfo(item) }}</a>
                  </template>
                  <template #avatar>
                    <a-avatar :style="{ backgroundColor: getLogLevelColor(item.level) }">
                      {{ getLogLevelInitial(item.level) }}
                    </a-avatar>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>
      <a-col :span="8" class="dashboard-col">
        <a-card title="Popular Dishes" class="full-height-card popular-dishes-card">
          <template #extra>
            <a-tabs 
              v-model:activeKey="activeTabKey" 
              @change="onTabChange" 
              size="small" 
              :tabBarStyle="{ marginBottom: 0, borderBottom: 'none' }"
            >
              <a-tab-pane key="today" tab="Today" />
              <a-tab-pane key="history" tab="History" />
            </a-tabs>
          </template>
          <a-list
            item-layout="horizontal"
            :data-source="popularDishes"
          >
            <template #renderItem="{ item, index }">
              <a-list-item>
                <a-list-item-meta
                  :title="item.name"
                  :description="`Ordered ${item.count} times`"
                >
                  <template #avatar>
                    <a-avatar :style="{ backgroundColor: index < 3 ? '#ff4d4f' : '#1890ff' }">
                      {{ index + 1 }}
                    </a-avatar>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>
      <a-col :span="8" class="dashboard-col">
        <a-card title="AI Analyze" class="full-height-card">
          <template #extra>
            <a-button 
              type="primary" 
              size="small" 
              :loading="isAnalyzing"
              @click="analyzeData"
            >
              Analyze
            </a-button>
          </template>
          <div v-if="!aiAnalysisResult && !isAnalyzing" class="empty-analysis">
            <a-icon type="robot" />
            <p>Click analyze to get AI insights</p>
          </div>
          <div v-else-if="isAnalyzing" class="analyzing-container">
            <a-spin size="large" />
            <p>Analyzing data...</p>
          </div>
          <div v-else class="analysis-content" v-html="parsedAiAnalysis"></div>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import { dataInsightApi } from '../services/api';
import { marked } from 'marked';

export default {
  name: 'DashboardView',
  data() {
    return {
      stats: {
        totalUsers: 0,
        totalDishes: 0,
        totalInteractions: 0,
        dailyActiveUsers: 0,
      },
      recentActivity: [],
      popularDishes: [],
      activeTabKey: 'today',
      isAnalyzing: false,
      aiAnalysisResult: '',
    };
  },
  computed: {
    parsedAiAnalysis() {
      return this.aiAnalysisResult ? marked.parse(this.aiAnalysisResult) : '';
    }
  },
  async mounted() {
    await this.loadDashboardData();
  },
  methods: {
    async fetchPopularDishes() {
      try {
        let startDate = null;
        let endDate = null;

        if (this.activeTabKey === 'today') {
          const now = new Date();
          const start = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0, 0);
          const end = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59, 999);
          startDate = start.toISOString();
          endDate = end.toISOString();
        }

        const dishesResponse = await dataInsightApi.getPopularDishes(5, this.activeTabKey, startDate, endDate);
        this.popularDishes = dishesResponse.data;
      } catch (error) {
        console.error('Error fetching popular dishes:', error);
      }
    },
    onTabChange(key) {
      this.activeTabKey = key;
      this.fetchPopularDishes();
    },
    async loadDashboardData() {
      try {
        const statsResponse = await dataInsightApi.getStats();
        this.stats = statsResponse.data;

        const activityResponse = await dataInsightApi.getRecentActivity();
        this.recentActivity = activityResponse.data;

        await this.fetchPopularDishes();
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        this.$message?.error('Failed to load dashboard data');
      }
    },
    getUserInfo(item) {
      if (item.userId?.name) return item.userId.name;
      if (item.userId?.uid) return item.userId.uid;
      if (item.extra?.uid) return item.extra.uid;
      if (item.userId) return item.userId;
      return 'Unknown User';
    },
    getUserInitials(item) {
      const userInfo = this.getUserInfo(item);
      if (userInfo && userInfo !== 'Unknown User') {
        return userInfo.charAt(0).toUpperCase();
      }
      return '?';
    },
    getActionValue(item) {
      if (item.action) return item.action;
      if (item.extra?.action) return item.extra.action;
      return 'N/A';
    },
    getLogLevelColor(level) {
      // 根据日志级别返回不同颜色
      const levelColors = {
        'DEBUG': '#87CEEB',    // 浅蓝色
        'INFO': '#1890ff',     // 蓝色
        'WARNING': '#faad14',  // 橙色
        'ERROR': '#f5222d',    // 红色
        'CRITICAL': '#a61d24', // 深红色
        'SUCCESS': '#52c41a'   // 绿色
      };
      return levelColors[level?.toUpperCase()] || '#1890ff'; // 默认蓝色
    },
    getLogLevelInitial(level) {
      // 获取日志级别的首字母
      if (!level) return '?';
      return level.charAt(0).toUpperCase();
    },
    async analyzeData() {
      this.isAnalyzing = true;
      try {
        const response = await dataInsightApi.getAiAnalysis();
        this.aiAnalysisResult = response.data.analysis;
      } catch (error) {
        console.error('AI Analysis failed:', error);
        this.$message?.error('AI Analysis failed. Please try again.');
        this.aiAnalysisResult = "Analysis failed. Please try again later.";
      } finally {
        this.isAnalyzing = false;
      }
    }
  }
};
</script>

<style scoped>
:deep(.ant-tabs-nav-more) {
  display: none !important;
}

.dashboard-row {
  height: 460px;
}

.dashboard-col {
  height: 100%;
}

.stats-card {
  min-height: auto;
}

.stats-card :deep(.ant-card-body) {
  padding: 10px 20px 10px 20px;
}

/* 调整 stats-card 中的段落间距 */
.stats-card :deep(.ant-card-body p) {
  margin-bottom: 6px; /* 减少段落之间的间距 */
}

.full-height-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.full-height-card :deep(.ant-card-body) {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

/* Recent Activity 和 Popular Dishes 的列表样式 */
.full-height-card :deep(.ant-list) {
  flex: 1;
  overflow-y: hidden; /* 禁止滚动 */
  padding: 12px; /* 恢复之前的值 */
}

/* Recent Activity 和 Popular Dishes 隐藏滚动条 */
.recent-activity-card :deep(.ant-list),
.popular-dishes-card :deep(.ant-list) {
  flex: 1;
  overflow-y: hidden; /* 禁止滚动 */
  padding: 12px;
  /* 隐藏滚动条 */
  -ms-overflow-style: none;  /* IE 和 Edge */
  scrollbar-width: none;  /* Firefox */
}

.recent-activity-card :deep(.ant-list::-webkit-scrollbar),
.popular-dishes-card :deep(.ant-list::-webkit-scrollbar) {
  display: none; /* Chrome, Safari, Opera */
}

.full-height-card :deep(.ant-list-pagination) {
  padding: 12px; /* 恢复之前的值 */
  margin: 0;
}

.activity-time {
  font-size: 12px;
  color: #999;
  margin-top: 2px; /* 减少时间显示的上边距 */
}

/* Recent Activity 列表项样式调整 */
.recent-activity-card :deep(.ant-list-item) {
  padding: 6px 12px !important; /* 减少列表项的内边距 */
}

.recent-activity-card :deep(.ant-list-item-meta) {
  margin-bottom: 0; /* 移除列表项元信息的底部边距 */
}

.recent-activity-card :deep(.ant-list-item-meta-title) {
  margin-bottom: 2px; /* 减少标题的底部边距 */
}

.recent-activity-card :deep(.ant-list-item-meta-description) {
  margin-bottom: 0; /* 移除描述的底部边距 */
}

/* Recent Activity 文本不换行，超出显示省略号 */
.recent-activity-card :deep(.ant-list-item-meta-title),
.recent-activity-card :deep(.ant-list-item-meta-description) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.popular-dishes-card :deep(.ant-list-item) {
  padding: 12px !important; /* 保持列表项内边距 */
}

.popular-dishes-card :deep(.ant-list-item-meta) {
  margin-bottom: 0; /* 保持元信息底部边距 */
}

.popular-dishes-card :deep(.ant-list-item-meta-title) {
  margin-bottom: 2px; /* 调整标题底部边距以保持一致性 */
}

.popular-dishes-card :deep(.ant-list-item-meta-description) {
  margin-bottom: 0; /* 保持描述底部边距 */
}

/* Popular Dishes 文本不换行，超出显示省略号 */
.popular-dishes-card :deep(.ant-list-item-meta-title),
.popular-dishes-card :deep(.ant-list-item-meta-description) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* AI Analyze 区域样式 */
.empty-analysis {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
  color: #999;
  text-align: center;
}

.empty-analysis .anticon {
  font-size: 48px;
  margin-bottom: 16px;
  color: #d9d9d9;
}

.analyzing-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 40px 20px;
}

.analysis-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  font-size: 16px;
  min-height: 0; /* Ensures flex child can shrink */
}

.analysis-content :deep(p) {
  margin-bottom: 10px;
  line-height: 1.5;
}

.analysis-content :deep(ul), 
.analysis-content :deep(ol) {
  padding-left: 20px;
  margin-bottom: 10px;
}

.analysis-content :deep(strong) {
  font-weight: 600;
  color: #1890ff;
}
</style>