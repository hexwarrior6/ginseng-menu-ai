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
              <template v-if="column.dataIndex === 'uid'">
                {{ record.uid }}
              </template>

              <template v-else-if="column.dataIndex === 'dietaryRestrictions'">
                <a-tag v-for="restriction in record.preferences?.dietary_restrictions || []" :key="restriction" color="orange">
                  {{ restriction }}
                </a-tag>
                <span v-if="!(record.preferences?.dietary_restrictions && record.preferences?.dietary_restrictions.length)">No restrictions</span>
              </template>

              <template v-else-if="column.dataIndex === 'favoriteCuisines'">
                <a-tag v-for="cuisine in record.preferences?.favorite_cuisines || []" :key="cuisine" color="green">
                  {{ cuisine }}
                </a-tag>
                <span v-if="!(record.preferences?.favorite_cuisines && record.preferences?.favorite_cuisines.length)">No favorite cuisines</span>
              </template>

              <template v-else-if="column.dataIndex === 'allergies'">
                <a-tag v-for="allergy in record.preferences?.allergies || []" :key="allergy" color="red">
                  {{ allergy }}
                </a-tag>
                <span v-if="!(record.preferences?.allergies && record.preferences?.allergies.length)">No allergies</span>
              </template>

              <template v-else-if="column.dataIndex === 'lastActive'">
                {{ record.last_active ? new Date(record.last_active).toLocaleString() : 'Never' }}
              </template>

              <template v-else-if="column.dataIndex === 'createdAt'">
                {{ record.created_at ? new Date(record.created_at).toLocaleString() : 'N/A' }}
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
        <a-descriptions-item label="UID">{{ selectedUser.uid }}</a-descriptions-item>
        <a-descriptions-item label="Dietary Restrictions">
          <a-space wrap>
            <a-tag v-for="restriction in selectedUser.preferences?.dietary_restrictions || []" :key="restriction" color="orange">
              {{ restriction }}
            </a-tag>
            <span v-if="!(selectedUser.preferences?.dietary_restrictions && selectedUser.preferences?.dietary_restrictions.length)">No restrictions</span>
          </a-space>
        </a-descriptions-item>
        <a-descriptions-item label="Favorite Cuisines">
          <a-space wrap>
            <a-tag v-for="cuisine in selectedUser.preferences?.favorite_cuisines || []" :key="cuisine" color="green">
              {{ cuisine }}
            </a-tag>
            <span v-if="!(selectedUser.preferences?.favorite_cuisines && selectedUser.preferences?.favorite_cuisines.length)">No favorite cuisines</span>
          </a-space>
        </a-descriptions-item>
        <a-descriptions-item label="Allergies">
          <a-space wrap>
            <a-tag v-for="allergy in selectedUser.preferences?.allergies || []" :key="allergy" color="red">
              {{ allergy }}
            </a-tag>
            <span v-if="!(selectedUser.preferences?.allergies && selectedUser.preferences?.allergies.length)">No allergies</span>
          </a-space>
        </a-descriptions-item>
        <a-descriptions-item label="Created At">
          {{ selectedUser.created_at ? new Date(selectedUser.created_at).toLocaleString() : 'N/A' }}
        </a-descriptions-item>
        <a-descriptions-item label="Last Active">
          {{ selectedUser.last_active ? new Date(selectedUser.last_active).toLocaleString() : 'Never' }}
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
          title: 'UID',
          dataIndex: 'uid',
          key: 'uid',
          sorter: (a, b) => (a.uid || '').localeCompare(b.uid || ''),
        },
        {
          title: 'Dietary Restrictions',
          dataIndex: 'dietaryRestrictions',
          key: 'dietaryRestrictions',
        },
        {
          title: 'Favorite Cuisines',
          dataIndex: 'favoriteCuisines',
          key: 'favoriteCuisines',
        },
        {
          title: 'Allergies',
          dataIndex: 'allergies',
          key: 'allergies',
        },
        {
          title: 'Created At',
          dataIndex: 'createdAt',
          key: 'createdAt',
        },
        {
          title: 'Last Active',
          dataIndex: 'lastActive',
          key: 'lastActive',
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