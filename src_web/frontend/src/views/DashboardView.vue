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

    <a-row :gutter="[16, 16]" style="margin-top: 16px;">
      <a-col :span="12">
        <a-card title="Recent Activity">
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
      <a-col :span="12">
        <a-card 
          :tab-list="tabList"
          :active-tab-key="activeTabKey"
          @tabChange="onTabChange"
        >
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
    </a-row>
  </div>
</template>

<script>
import { dataInsightApi } from '../services/api';

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
      tabList: [
        {
          key: 'today',
          tab: 'Today',
        },
        {
          key: 'history',
          tab: 'History',
        },
      ],
    };
  },
  async mounted() {
    await this.loadDashboardData();
  },
  methods: {
    async fetchPopularDishes() {
      try {
        const dishesResponse = await dataInsightApi.getPopularDishes(5, this.activeTabKey);
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
        // Fetch dashboard stats
        const statsResponse = await dataInsightApi.getStats();
        this.stats = statsResponse.data;

        // Fetch recent activity
        const activityResponse = await dataInsightApi.getRecentActivity();
        this.recentActivity = activityResponse.data;

        // Fetch popular dishes
        await this.fetchPopularDishes();
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Show error notification to user
        this.$message?.error('Failed to load dashboard data');
      }
    },
    getUserInfo(item) {
      // Try to get user info from different possible fields
      if (item.userId?.name) return item.userId.name;
      if (item.userId?.uid) return item.userId.uid;
      if (item.extra?.uid) return item.extra.uid;
      if (item.userId) return item.userId; // In case it's just a UID string
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
      // Try to get action from different possible fields
      if (item.action) return item.action;
      if (item.extra?.action) return item.extra.action;
      return 'N/A';
    }
  }
};
</script>
