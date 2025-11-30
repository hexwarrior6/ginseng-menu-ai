<template>
  <div>
    <a-row :gutter="[16, 16]">
      <a-col :span="24">
        <a-card title="Dishes Management">
          <template #extra>
            <a-space>
              <a-button type="primary" @click="loadDishes">
                <template #icon>
                  <ReloadOutlined />
                </template>
                Refresh
              </a-button>
              <a-button type="primary" @click="showAddModal">
                <template #icon>
                  <PlusOutlined />
                </template>
                Add Dish
              </a-button>
            </a-space>
          </template>
          
          <a-table
            :columns="columns"
            :data-source="dishes"
            :loading="loading"
            row-key="_id"
            :pagination="{ pageSize: 10 }"
          >
            <template #bodyCell="{ column, text, record }">
              <template v-if="column.dataIndex === 'name'">
                {{ record.name }}
              </template>

              <template v-else-if="column.dataIndex === 'category'">
                <a-tag color="blue">{{ record.category || 'Uncategorized' }}</a-tag>
              </template>

              <template v-else-if="column.dataIndex === 'calories'">
                {{ record.calories || 'N/A' }} cal
              </template>

              <template v-else-if="column.dataIndex === 'protein'">
                {{ record.nutrition?.protein_g || 'N/A' }}g
              </template>

              <template v-else-if="column.dataIndex === 'carbs'">
                {{ record.nutrition?.carbs_g || 'N/A' }}g
              </template>

              <template v-else-if="column.dataIndex === 'fat'">
                {{ record.nutrition?.fat_g || 'N/A' }}g
              </template>

              <template v-else-if="column.dataIndex === 'fiber'">
                {{ record.nutrition?.fiber_g || 'N/A' }}g
              </template>

              <template v-else-if="column.dataIndex === 'timestamp'">
                {{ record.timestamp ? new Date(record.timestamp).toLocaleString() : 'N/A' }}
              </template>

              <template v-else-if="column.dataIndex === 'actions'">
                <a-space>
                  <a-button type="link" size="small" @click="viewDish(record)">View</a-button>
                  <a-button type="link" size="small" @click="editDish(record)">Edit</a-button>
                  <a-popconfirm
                    title="Are you sure you want to delete this dish?"
                    ok-text="Yes"
                    cancel-text="No"
                    @confirm="deleteDish(record._id)"
                  >
                    <a-button type="link" size="small" danger>Delete</a-button>
                  </a-popconfirm>
                </a-space>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>
    </a-row>
    
    <!-- Dish Detail Modal -->
    <a-modal
      v-model:open="dishDetailVisible"
      title="Dish Details"
      :footer="null"
      width="700px"
    >
      <a-descriptions v-if="selectedDish" :column="1" bordered>
        <a-descriptions-item label="ID">{{ selectedDish._id }}</a-descriptions-item>
        <a-descriptions-item label="Name">{{ selectedDish.name }}</a-descriptions-item>
        <a-descriptions-item label="Category">
          <a-tag color="blue">{{ selectedDish.category || 'Uncategorized' }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="Timestamp">
          {{ selectedDish.timestamp ? new Date(selectedDish.timestamp).toLocaleString() : 'N/A' }}
        </a-descriptions-item>
        <a-descriptions-item label="Calories">
          {{ selectedDish.calories || 'N/A' }} cal
        </a-descriptions-item>
        <a-descriptions-item label="Nutrition Facts">
          <div v-if="selectedDish.nutrition">
            <p><strong>Protein:</strong> {{ selectedDish.nutrition.protein_g || 'N/A' }}g</p>
            <p><strong>Carbs:</strong> {{ selectedDish.nutrition.carbs_g || 'N/A' }}g</p>
            <p><strong>Fat:</strong> {{ selectedDish.nutrition.fat_g || 'N/A' }}g</p>
            <p><strong>Fiber:</strong> {{ selectedDish.nutrition.fiber_g || 'N/A' }}g</p>
          </div>
          <span v-else>No nutrition facts available</span>
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
    
    <!-- Add/Edit Dish Modal -->
    <a-modal
      v-model:open="dishFormVisible"
      :title="isEditing ? 'Edit Dish' : 'Add New Dish'"
      @ok="saveDish"
      :confirm-loading="formLoading"
    >
      <a-form
        :model="currentDish"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 18 }"
      >
        <a-form-item label="Name" :rules="[{ required: true, message: 'Please input dish name!' }]">
          <a-input v-model:value="currentDish.name" />
        </a-form-item>
        <a-form-item label="Category">
          <a-input v-model:value="currentDish.category" />
        </a-form-item>
        <a-form-item label="Calories">
          <a-input-number v-model:value="currentDish.calories" style="width: 100%" />
        </a-form-item>
        <a-form-item label="Protein (g)">
          <a-input-number v-model:value="currentDish.nutrition.protein_g" style="width: 100%" />
        </a-form-item>
        <a-form-item label="Carbs (g)">
          <a-input-number v-model:value="currentDish.nutrition.carbs_g" style="width: 100%" />
        </a-form-item>
        <a-form-item label="Fat (g)">
          <a-input-number v-model:value="currentDish.nutrition.fat_g" style="width: 100%" />
        </a-form-item>
        <a-form-item label="Fiber (g)">
          <a-input-number v-model:value="currentDish.nutrition.fiber_g" style="width: 100%" />
        </a-form-item>
        <a-form-item label="Timestamp">
          <a-date-picker v-model:value="currentDish.timestamp" show-time style="width: 100%" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script>
import { dishApi } from '../services/api';
import { ReloadOutlined, PlusOutlined } from '@ant-design/icons-vue';
import { DatePicker } from 'ant-design-vue';
import dayjs from 'dayjs';

export default {
  name: 'DishesView',
  components: {
    ReloadOutlined,
    PlusOutlined,
    'a-date-picker': DatePicker
  },
  setup() {
    return {
      dayjs,
    };
  },
  data() {
    return {
      dishes: [],
      loading: false,
      dishDetailVisible: false,
      dishFormVisible: false,
      formLoading: false,
      selectedDish: null,
      currentDish: {
        nutrition: {}
      },
      isEditing: false,
      columns: [
        {
          title: 'Name',
          dataIndex: 'name',
          key: 'name',
          sorter: (a, b) => a.name.localeCompare(b.name),
        },
        {
          title: 'Category',
          dataIndex: 'category',
          key: 'category',
        },
        {
          title: 'Calories',
          dataIndex: 'calories',
          key: 'calories',
          sorter: (a, b) => (a.calories || 0) - (b.calories || 0),
        },
        {
          title: 'Protein (g)',
          dataIndex: 'protein',
          key: 'protein',
        },
        {
          title: 'Carbs (g)',
          dataIndex: 'carbs',
          key: 'carbs',
        },
        {
          title: 'Fat (g)',
          dataIndex: 'fat',
          key: 'fat',
        },
        {
          title: 'Fiber (g)',
          dataIndex: 'fiber',
          key: 'fiber',
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
    await this.loadDishes();
  },
  methods: {
    async loadDishes() {
      this.loading = true;
      try {
        const response = await dishApi.getAll();
        this.dishes = response.data;
      } catch (error) {
        console.error('Error fetching dishes:', error);
        this.$message?.error('Failed to load dishes');
      } finally {
        this.loading = false;
      }
    },
    viewDish(dish) {
      this.selectedDish = dish;
      this.dishDetailVisible = true;
    },
    showAddModal() {
      this.currentDish = {
        name: '',
        category: '',
        calories: null,
        nutrition: {
          protein_g: null,
          carbs_g: null,
          fat_g: null,
          fiber_g: null
        },
        timestamp: null
      };
      this.isEditing = false;
      this.dishFormVisible = true;
    },
    editDish(dish) {
      this.currentDish = {
        ...dish,
        nutrition: {
          ...dish.nutrition
        },
        timestamp: dish.timestamp ? dayjs(new Date(dish.timestamp)) : null
      };
      this.isEditing = true;
      this.dishFormVisible = true;
    },
    async saveDish() {
      this.formLoading = true;
      try {
        // Prepare payload with proper timestamp conversion
        let payload = { ...this.currentDish };

        // Convert timestamp from dayjs object to ISO string if it exists
        if (payload.timestamp) {
          payload.timestamp = payload.timestamp.$d ? new Date(payload.timestamp.$d) : payload.timestamp;
        }

        // Ensure nutrition object exists and has proper values
        if (!payload.nutrition) {
          payload.nutrition = {};
        }

        if (this.isEditing) {
          await dishApi.update(this.currentDish._id, payload);
          this.$message?.success('Dish updated successfully');
        } else {
          await dishApi.create(payload);
          this.$message?.success('Dish added successfully');
        }

        this.dishFormVisible = false;
        await this.loadDishes();
      } catch (error) {
        console.error('Error saving dish:', error);
        this.$message?.error('Failed to save dish');
      } finally {
        this.formLoading = false;
      }
    },
    async deleteDish(id) {
      try {
        await dishApi.delete(id);
        this.$message?.success('Dish deleted successfully');
        await this.loadDishes();
      } catch (error) {
        console.error('Error deleting dish:', error);
        this.$message?.error('Failed to delete dish');
      }
    }
  }
};
</script>