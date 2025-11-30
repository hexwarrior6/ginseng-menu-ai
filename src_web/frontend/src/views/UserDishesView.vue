<template>
  <div>
    <a-row :gutter="[16, 16]">
      <a-col :span="24">
        <a-card title="User Dish Selections">
          <template #extra>
            <a-space>
              <a-input-search
                v-model:value="searchUid"
                placeholder="Search by UID"
                @search="searchByUid"
                style="width: 300px"
              />
              <a-button type="primary" @click="loadUserDishes">
                <template #icon>
                  <ReloadOutlined />
                </template>
                Refresh
              </a-button>
            </a-space>
          </template>

          <a-table
            :columns="columns"
            :data-source="userDishes"
            :loading="loading"
            row-key="_id"
            :pagination="{ pageSize: 10 }"
          >
            <template #bodyCell="{ column, text, record }">
              <template v-if="column.dataIndex === 'uid'">
                {{ record.uid }}
              </template>

              <template v-else-if="column.dataIndex === 'dish_name'">
                {{ record.dish_name }}
              </template>

              <template v-else-if="column.dataIndex === 'timestamp'">
                {{ record.timestamp ? new Date(record.timestamp).toLocaleString() : 'N/A' }}
              </template>

              <template v-else-if="column.dataIndex === 'actions'">
                <a-popconfirm
                  title="Are you sure you want to delete this record?"
                  ok-text="Yes"
                  cancel-text="No"
                  @confirm="deleteUserDish(record._id)"
                >
                  <a-button type="link" size="small" danger>Delete</a-button>
                </a-popconfirm>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script>
import { userDishApi } from '../services/api';
import { ReloadOutlined } from '@ant-design/icons-vue';

export default {
  name: 'UserDishesView',
  components: {
    ReloadOutlined
  },
  data() {
    return {
      userDishes: [],
      loading: false,
      searchUid: '',
      columns: [
        {
          title: 'UID',
          dataIndex: 'uid',
          key: 'uid',
          sorter: (a, b) => (a.uid || '').localeCompare(b.uid || ''),
        },
        {
          title: 'Dish Name',
          dataIndex: 'dish_name',
          key: 'dish_name',
          sorter: (a, b) => (a.dish_name || '').localeCompare(b.dish_name || ''),
        },
        {
          title: 'Timestamp',
          dataIndex: 'timestamp',
          key: 'timestamp',
          sorter: (a, b) => new Date(a.timestamp || 0) - new Date(b.timestamp || 0),
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
    await this.loadUserDishes();
  },
  methods: {
    async loadUserDishes() {
      this.loading = true;
      try {
        const response = await userDishApi.getAll();
        this.userDishes = response.data;
      } catch (error) {
        console.error('Error fetching user dishes:', error);
        this.$message?.error('Failed to load user dish selections');
      } finally {
        this.loading = false;
      }
    },
    async searchByUid(uid) {
      if (uid.trim()) {
        this.loading = true;
        try {
          const response = await userDishApi.getByUid(uid);
          this.userDishes = response.data;
        } catch (error) {
          console.error('Error fetching user dishes by UID:', error);
          this.$message?.error('Failed to load user dish selections');
        } finally {
          this.loading = false;
        }
      } else {
        await this.loadUserDishes();
      }
    },
    async deleteUserDish(id) {
      try {
        await userDishApi.delete(id);
        this.$message?.success('Record deleted successfully');
        await this.loadUserDishes();
      } catch (error) {
        console.error('Error deleting user dish:', error);
        this.$message?.error('Failed to delete record');
      }
    }
  }
};
</script>