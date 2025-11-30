<template>
  <div>
    <a-row :gutter="[16, 16]">
      <a-col :span="24">
        <a-card title="Users Management">
          <template #extra>
            <a-space>
              <a-button type="primary" @click="loadUsers">
                <template #icon>
                  <ReloadOutlined />
                </template>
                Refresh
              </a-button>
            </a-space>
          </template>
          
          <a-table 
            :columns="columns" 
            :data-source="users" 
            :loading="loading"
            row-key="_id"
            :pagination="{ pageSize: 10 }"
          >
            <template #bodyCell="{ column, text, record }">
              <template v-if="column.dataIndex === 'preferences'">
                <a-tag v-for="pref in record.preferences || []" :key="pref" color="blue">
                  {{ pref }}
                </a-tag>
                <span v-if="!(record.preferences && record.preferences.length)">No preferences</span>
              </template>
              
              <template v-else-if="column.dataIndex === 'dietaryRestrictions'">
                <a-tag v-for="restriction in record.dietaryRestrictions || []" :key="restriction" color="orange">
                  {{ restriction }}
                </a-tag>
                <span v-if="!(record.dietaryRestrictions && record.dietaryRestrictions.length)">No restrictions</span>
              </template>
              
              <template v-else-if="column.dataIndex === 'isActive'">
                <a-tag :color="record.isActive ? 'green' : 'red'">
                  {{ record.isActive ? 'Active' : 'Inactive' }}
                </a-tag>
              </template>
              
              <template v-else-if="column.dataIndex === 'lastLogin'">
                {{ record.lastLogin ? new Date(record.lastLogin).toLocaleString() : 'Never' }}
              </template>
              
              <template v-else-if="column.dataIndex === 'actions'">
                <a-space>
                  <a-button type="link" size="small" @click="viewUser(record)">View</a-button>
                  <a-button type="link" size="small" @click="editUser(record)">Edit</a-button>
                </a-space>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>
    </a-row>
    
    <!-- User Detail Modal -->
    <a-modal 
      v-model:open="userDetailVisible" 
      title="User Details" 
      :footer="null"
      width="600px"
    >
      <a-descriptions v-if="selectedUser" :column="1" bordered>
        <a-descriptions-item label="ID">{{ selectedUser._id }}</a-descriptions-item>
        <a-descriptions-item label="Name">{{ selectedUser.name }}</a-descriptions-item>
        <a-descriptions-item label="Email">{{ selectedUser.email }}</a-descriptions-item>
        <a-descriptions-item label="Active Status">
          <a-tag :color="selectedUser.isActive ? 'green' : 'red'">
            {{ selectedUser.isActive ? 'Active' : 'Inactive' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="Last Login">
          {{ selectedUser.lastLogin ? new Date(selectedUser.lastLogin).toLocaleString() : 'Never' }}
        </a-descriptions-item>
        <a-descriptions-item label="Preferences">
          <a-space wrap>
            <a-tag v-for="pref in selectedUser.preferences || []" :key="pref" color="blue">
              {{ pref }}
            </a-tag>
            <span v-if="!(selectedUser.preferences && selectedUser.preferences.length)">No preferences</span>
          </a-space>
        </a-descriptions-item>
        <a-descriptions-item label="Dietary Restrictions">
          <a-space wrap>
            <a-tag v-for="restriction in selectedUser.dietaryRestrictions || []" :key="restriction" color="orange">
              {{ restriction }}
            </a-tag>
            <span v-if="!(selectedUser.dietaryRestrictions && selectedUser.dietaryRestrictions.length)">No restrictions</span>
          </a-space>
        </a-descriptions-item>
        <a-descriptions-item label="Created At">
          {{ new Date(selectedUser.createdAt).toLocaleString() }}
        </a-descriptions-item>
        <a-descriptions-item label="Updated At">
          {{ new Date(selectedUser.updatedAt).toLocaleString() }}
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script>
import { userApi } from '../services/api';
import { ReloadOutlined } from '@ant-design/icons-vue';

export default {
  name: 'UsersView',
  components: {
    ReloadOutlined
  },
  data() {
    return {
      users: [],
      loading: false,
      userDetailVisible: false,
      selectedUser: null,
      columns: [
        {
          title: 'Name',
          dataIndex: 'name',
          key: 'name',
          sorter: (a, b) => a.name.localeCompare(b.name),
        },
        {
          title: 'Email',
          dataIndex: 'email',
          key: 'email',
        },
        {
          title: 'Preferences',
          dataIndex: 'preferences',
          key: 'preferences',
        },
        {
          title: 'Dietary Restrictions',
          dataIndex: 'dietaryRestrictions',
          key: 'dietaryRestrictions',
        },
        {
          title: 'Status',
          dataIndex: 'isActive',
          key: 'isActive',
        },
        {
          title: 'Last Login',
          dataIndex: 'lastLogin',
          key: 'lastLogin',
        },
        {
          title: 'Actions',
          dataIndex: 'actions',
          key: 'actions',
        }
      ],
    };
  },
  async mounted() {
    await this.loadUsers();
  },
  methods: {
    async loadUsers() {
      this.loading = true;
      try {
        const response = await userApi.getAll();
        this.users = response.data;
      } catch (error) {
        console.error('Error fetching users:', error);
        this.$message?.error('Failed to load users');
      } finally {
        this.loading = false;
      }
    },
    viewUser(user) {
      this.selectedUser = user;
      this.userDetailVisible = true;
    },
    editUser(user) {
      // In a real app, this would open an edit form
      this.$message?.info('Edit functionality would be implemented here');
    }
  }
};
</script>