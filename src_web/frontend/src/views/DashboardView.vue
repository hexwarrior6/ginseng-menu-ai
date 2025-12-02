<template>
  <div>
    <a-row :gutter="[16, 16]">
      <a-col :span="24">
        <h1>Dashboard</h1>
      </a-col>
    </a-row>

    <a-row :gutter="[16, 16]">
      <a-col :span="6">
        <a-card title="Total Users">
          <template #extra>
            <a-tag color="blue">Users</a-tag>
          </template>
          <p style="font-size: 24px; font-weight: bold;">{{ stats.totalUsers }}</p>
          <p><a-icon type="user" /> Total registered users</p>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card title="Total Dishes Today">
          <template #extra>
            <a-tag color="green">Dishes</a-tag>
          </template>
          <p style="font-size: 24px; font-weight: bold;">{{ stats.totalDishes }}</p>
          <p><a-icon type="appstore" /> Available dishes</p>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card title="Total Interactions">
          <template #extra>
            <a-tag color="orange">Interactions</a-tag>
          </template>
          <p style="font-size: 24px; font-weight: bold;">{{ stats.totalInteractions }}</p>
          <p><a-icon type="interaction" /> User interactions</p>
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card title="Daily Active Users">
          <template #extra>
            <a-tag color="purple">Today</a-tag>
          </template>
          <p style="font-size: 24px; font-weight: bold;">{{ stats.dailyActiveUsers }}</p>
          <p><a-icon type="team" /> Active today</p>
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="[16, 16]" style="margin-top: 16px;" class="dashboard-row">
      <a-col :span="8">
        <a-card title="Recent Activity" class="full-height-card">
          <a-list
            item-layout="horizontal"
            :data-source="recentActivity"
            :pagination="{
              pageSize: 5,
            }"
          >
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta
                  :description="`${getActionValue(item)} - ${new Date(item.timestamp).toLocaleString()}`"
                >
                  <template #title>
                    <a>{{ getUserInfo(item) }}</a>
                  </template>
                  <template #avatar>
                    <a-avatar :style="{ backgroundColor: '#1890ff' }">
                      {{ getUserInitials(item) }}
                    </a-avatar>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card title="Popular Dishes" class="full-height-card">
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
      <a-col :span="8">
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
  min-height: 400px;
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
  overflow-y: auto;
  padding: 16px;
}

.full-height-card :deep(.ant-list-pagination) {
  padding: 16px;
  margin: 0;
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
  max-height: 100%;
  font-size: 16px;
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