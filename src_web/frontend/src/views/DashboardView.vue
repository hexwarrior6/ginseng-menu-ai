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
                  :description="`${item.action} - ${new Date(item.createdAt).toLocaleString()}`"
                >
                  <template #title>
                    <a>{{ item.userId?.name || item.userId?.uid || 'Unknown User' }}</a>
                  </template>
                  <template #avatar>
                    <a-avatar :style="{ backgroundColor: '#1890ff' }">
                      {{ (item.userId?.name || item.userId?.uid)?.charAt(0) || '?' }}
                    </a-avatar>
                  </template>
                </a-list-item-meta>
              </a-list-item>
            </template>
          </a-list>
        </a-card>
      </a-col>
      <a-col :span="12">
        <a-card title="Popular Dishes">
          <a-list
            item-layout="horizontal"
            :data-source="popularDishes"
          >
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta
                  :title="item.name"
                  :description="item.description || 'No description'"
                >
                  <template #avatar>
                    <a-avatar shape="square" v-if="item.image" :src="item.image" />
                    <a-avatar v-else :style="{ backgroundColor: '#87d068' }">
                      <icon-appstore />
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
      popularDishes: []
    };
  },
  async mounted() {
    await this.loadDashboardData();
  },
  methods: {
    async loadDashboardData() {
      try {
        // Fetch dashboard stats
        const statsResponse = await dataInsightApi.getStats();
        this.stats = statsResponse.data;

        // Fetch recent activity
        const activityResponse = await dataInsightApi.getRecentActivity();
        this.recentActivity = activityResponse.data;

        // Fetch popular dishes
        const dishesResponse = await dataInsightApi.getPopularDishes();
        this.popularDishes = dishesResponse.data;
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Show error notification to user
        this.$message?.error('Failed to load dashboard data');
      }
    }
  }
};
</script>
