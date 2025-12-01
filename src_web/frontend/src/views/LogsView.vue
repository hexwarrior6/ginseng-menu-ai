<template>
  <div>
    <a-row :gutter="[16, 16]">
      <a-col :span="24">
        <a-card title="Interaction Logs">
          <template #extra>
            <a-space>
              <a-button type="primary" @click="loadLogs">
                <template #icon>
                  <ReloadOutlined />
                </template>
                Refresh
              </a-button>
              <a-range-picker 
                v-model:value="dateRange" 
                @change="onDateChange"
                style="width: 250px"
              />
            </a-space>
          </template>
          
          <a-table
            :columns="columns"
            :data-source="logs"
            :loading="loading"
            row-key="_id"
            :pagination="{
              pageSize: 10,
              showSizeChanger: true,
              showQuickJumper: true,
              showTotal: (total) => `Total ${total} items`
            }"
          >
            <template #bodyCell="{ column, text, record }">
              <template v-if="column.dataIndex === 'userId'">
                <a-tag color="blue">{{ getUserInfo(record) }}</a-tag>
              </template>

              <template v-else-if="column.dataIndex === 'action'">
                <a-tag :color="getActionColor(getActionValue(record))">
                  {{ getActionValue(record) }}
                </a-tag>
              </template>

              <template v-else-if="column.dataIndex === 'actionType'">
                <a-tag color="orange">{{ record.actionType || record.extra?.module_name || 'N/A' }}</a-tag>
              </template>

              <template v-else-if="column.dataIndex === 'level'">
                <a-tag :color="getLevelColor(record.level)">{{ record.level }}</a-tag>
              </template>

              <template v-else-if="column.dataIndex === 'message'">
                {{ record.message }}
              </template>

              <template v-else-if="column.dataIndex === 'module'">
                {{ record.module || record.function || 'N/A' }}
              </template>

              <template v-else-if="column.dataIndex === 'dishName'">
                {{ record.dishName || 'N/A' }}
              </template>

              <template v-else-if="column.dataIndex === 'timestamp'">
                {{ new Date(record.timestamp).toLocaleString() }}
              </template>

              <template v-else-if="column.dataIndex === 'extra'">
                <a-popover placement="left" :title="'Extra Details'">
                  <template #content>
                    <pre style="max-width: 400px; white-space: pre-wrap;">{{ JSON.stringify(record.extra, null, 2) }}</pre>
                  </template>
                  <a-button type="link" size="small">View Extra</a-button>
                </a-popover>
              </template>

              <template v-else-if="column.dataIndex === 'details'">
                <a-popover placement="left" :title="'Details'">
                  <template #content>
                    <pre style="max-width: 400px; white-space: pre-wrap;">{{ JSON.stringify(record.details, null, 2) }}</pre>
                  </template>
                  <a-button type="link" size="small">View Details</a-button>
                </a-popover>
              </template>

              <template v-else-if="column.dataIndex === 'actions'">
                <a-popconfirm
                  title="Are you sure you want to delete this log?"
                  ok-text="Yes"
                  cancel-text="No"
                  @confirm="deleteLog(record._id)"
                >
                  <a-button type="link" size="small" danger>Delete</a-button>
                </a-popconfirm>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>
    </a-row>
    
    <!-- Log Detail Modal -->
    <a-modal
      v-model:open="logDetailVisible"
      title="Log Details"
      :footer="null"
      width="800px"
    >
      <a-descriptions v-if="selectedLog" :column="1" bordered>
        <a-descriptions-item label="ID">{{ selectedLog._id }}</a-descriptions-item>
        <a-descriptions-item label="User">{{ getUserInfo(selectedLog) }}</a-descriptions-item>
        <a-descriptions-item label="Level">
          <a-tag :color="getLevelColor(selectedLog.level)">{{ selectedLog.level }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="Message">{{ selectedLog.message }}</a-descriptions-item>
        <a-descriptions-item label="Module">{{ selectedLog.module || 'N/A' }}</a-descriptions-item>
        <a-descriptions-item label="Function">{{ selectedLog.function || 'N/A' }}</a-descriptions-item>
        <a-descriptions-item label="Timestamp">{{ new Date(selectedLog.timestamp).toLocaleString() }}</a-descriptions-item>
        <a-descriptions-item label="Process ID">{{ selectedLog.process_id || 'N/A' }}</a-descriptions-item>
        <a-descriptions-item label="Thread ID">{{ selectedLog.thread_id || 'N/A' }}</a-descriptions-item>
        <a-descriptions-item label="Thread Name">{{ selectedLog.thread_name || 'N/A' }}</a-descriptions-item>
        <a-descriptions-item label="Action">{{ getActionValue(selectedLog) }}</a-descriptions-item>
        <a-descriptions-item label="Action Type">{{ selectedLog.actionType || selectedLog.extra?.module_name || 'N/A' }}</a-descriptions-item>
        <a-descriptions-item label="Dish Name">{{ selectedLog.dishName || 'N/A' }}</a-descriptions-item>
        <a-descriptions-item label="Dish ID">{{ selectedLog.dishId || 'N/A' }}</a-descriptions-item>
        <a-descriptions-item label="IP Address">{{ selectedLog.ipAddress || 'N/A' }}</a-descriptions-item>
        <a-descriptions-item label="User Agent">{{ selectedLog.userAgent || 'N/A' }}</a-descriptions-item>
        <a-descriptions-item label="Extra Data">
          <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; white-space: pre-wrap;">
{{ JSON.stringify(selectedLog.extra || {}, null, 2) }}
          </pre>
        </a-descriptions-item>
        <a-descriptions-item label="Details">
          <pre style="background-color: #f5f5f5; padding: 10px; border-radius: 4px; white-space: pre-wrap;">
{{ JSON.stringify(selectedLog.details || {}, null, 2) }}
          </pre>
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script>
import { logApi } from '../services/api';
import { ReloadOutlined } from '@ant-design/icons-vue';
import { DatePicker } from 'ant-design-vue';

const { RangePicker } = DatePicker;

export default {
  name: 'LogsView',
  components: {
    ReloadOutlined,
    'a-range-picker': RangePicker
  },
  data() {
    return {
      logs: [],
      loading: false,
      logDetailVisible: false,
      selectedLog: null,
      dateRange: null,
      columns: [
        {
          title: 'Level',
          dataIndex: 'level',
          key: 'level',
          width: 80,
        },
        {
          title: 'User',
          dataIndex: 'userId',
          key: 'userId',
          width: 150,
        },
        {
          title: 'Action',
          dataIndex: 'action',
          key: 'action',
          width: 120,
        },
        {
          title: 'Action Type',
          dataIndex: 'actionType',
          key: 'actionType',
          width: 120,
        },
        {
          title: 'Module',
          dataIndex: 'module',
          key: 'module',
          width: 120,
        },
        {
          title: 'Message',
          dataIndex: 'message',
          key: 'message',
          ellipsis: true,
        },
        {
          title: 'Dish Name',
          dataIndex: 'dishName',
          key: 'dishName',
          ellipsis: true,
        },
        {
          title: 'Timestamp',
          dataIndex: 'timestamp',
          key: 'timestamp',
          width: 180,
          sorter: (a, b) => new Date(a.timestamp) - new Date(b.timestamp),
        },
        {
          title: 'Extra',
          dataIndex: 'extra',
          key: 'extra',
          width: 120,
        },
        {
          title: 'Details',
          dataIndex: 'details',
          key: 'details',
          width: 120,
        },
        {
          title: 'Actions',
          dataIndex: 'actions',
          key: 'actions',
          width: 100,
        }
      ],
    };
  },
  async mounted() {
    await this.loadLogs();
  },
  methods: {
    async loadLogs() {
      this.loading = true;
      try {
        const response = await logApi.getAll();
        this.logs = response.data;
      } catch (error) {
        console.error('Error fetching logs:', error);
        this.$message?.error('Failed to load logs');
      } finally {
        this.loading = false;
      }
    },
    getActionColor(action) {
      const colorMap = {
        'view': 'blue',
        'recommend': 'green',
        'select': 'orange',
        'purchase': 'gold',
        'rate': 'purple',
        'search': 'cyan',
        'filter': 'magenta'
      };
      return colorMap[action.toLowerCase()] || 'default';
    },
    getLevelColor(level) {
      const colorMap = {
        'INFO': 'blue',
        'DEBUG': 'cyan',
        'WARN': 'orange',
        'WARNING': 'orange',
        'ERROR': 'red',
        'CRITICAL': 'magenta'
      };
      return colorMap[level] || 'default';
    },
    getUserInfo(record) {
      // Try to get user info from different possible fields
      if (record.userId?.name) return record.userId.name;
      if (record.userId?.uid) return record.userId.uid;
      if (record.extra?.uid) return record.extra.uid;
      if (record.userId) return record.userId; // In case it's just a UID string
      return 'Unknown User';
    },
    getActionValue(record) {
      // Try to get action from different possible fields
      if (record.action) return record.action;
      if (record.extra?.action) return record.extra.action;
      return 'N/A';
    },
    viewLog(log) {
      this.selectedLog = log;
      this.logDetailVisible = true;
    },
    onDateChange(dates) {
      console.log('Date range changed:', dates);
      // In a real implementation, this would filter logs by date
    },
    async deleteLog(id) {
      try {
        await logApi.delete(id);
        this.$message?.success('Log deleted successfully');
        await this.loadLogs();
      } catch (error) {
        console.error('Error deleting log:', error);
        this.$message?.error('Failed to delete log');
      }
    }
  }
};
</script>