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
              <template v-if="column.dataIndex === 'isAvailable'">
                <a-tag :color="record.isAvailable ? 'green' : 'red'">
                  {{ record.isAvailable ? 'Available' : 'Not Available' }}
                </a-tag>
              </template>
              
              <template v-else-if="column.dataIndex === 'category'">
                <a-tag color="blue">{{ record.category || 'Uncategorized' }}</a-tag>
              </template>
              
              <template v-else-if="column.dataIndex === 'ingredients'">
                <a-tag v-for="ingredient in record.ingredients || []" :key="ingredient" color="orange">
                  {{ ingredient }}
                </a-tag>
                <span v-if="!(record.ingredients && record.ingredients.length)">No ingredients listed</span>
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
        <a-descriptions-item label="Description">{{ selectedDish.description || 'No description' }}</a-descriptions-item>
        <a-descriptions-item label="Category">
          <a-tag color="blue">{{ selectedDish.category || 'Uncategorized' }}</a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="Available Status">
          <a-tag :color="selectedDish.isAvailable ? 'green' : 'red'">
            {{ selectedDish.isAvailable ? 'Available' : 'Not Available' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="Ingredients">
          <a-space wrap>
            <a-tag v-for="ingredient in selectedDish.ingredients || []" :key="ingredient" color="orange">
              {{ ingredient }}
            </a-tag>
            <span v-if="!(selectedDish.ingredients && selectedDish.ingredients.length)">No ingredients listed</span>
          </a-space>
        </a-descriptions-item>
        <a-descriptions-item label="Nutritional Info">
          <div v-if="selectedDish.nutritionalInfo">
            <p><strong>Calories:</strong> {{ selectedDish.nutritionalInfo.calories || 'N/A' }}</p>
            <p><strong>Protein:</strong> {{ selectedDish.nutritionalInfo.protein || 'N/A' }}g</p>
            <p><strong>Carbs:</strong> {{ selectedDish.nutritionalInfo.carbs || 'N/A' }}g</p>
            <p><strong>Fat:</strong> {{ selectedDish.nutritionalInfo.fat || 'N/A' }}g</p>
          </div>
          <span v-else>No nutritional info</span>
        </a-descriptions-item>
        <a-descriptions-item label="Preparation Time">
          {{ selectedDish.preparationTime ? `${selectedDish.preparationTime} minutes` : 'N/A' }}
        </a-descriptions-item>
        <a-descriptions-item label="Image">
          <a-image v-if="selectedDish.image" :src="selectedDish.image" width="200" />
          <span v-else>No image</span>
        </a-descriptions-item>
        <a-descriptions-item label="Created At">
          {{ new Date(selectedDish.createdAt).toLocaleString() }}
        </a-descriptions-item>
        <a-descriptions-item label="Updated At">
          {{ new Date(selectedDish.updatedAt).toLocaleString() }}
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
        <a-form-item label="Description">
          <a-textarea v-model:value="currentDish.description" :rows="3" />
        </a-form-item>
        <a-form-item label="Category">
          <a-input v-model:value="currentDish.category" />
        </a-form-item>
        <a-form-item label="Ingredients">
          <a-textarea 
            v-model:value="currentDish.ingredientsStr" 
            placeholder="Enter ingredients separated by commas" 
            :rows="3"
          />
        </a-form-item>
        <a-form-item label="Available">
          <a-switch v-model:checked="currentDish.isAvailable" />
        </a-form-item>
        <a-form-item label="Prep Time (min)">
          <a-input-number v-model:value="currentDish.preparationTime" style="width: 100%" />
        </a-form-item>
        <a-form-item label="Image URL">
          <a-input v-model:value="currentDish.image" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script>
import { dishApi } from '../services/api';
import { ReloadOutlined, PlusOutlined } from '@ant-design/icons-vue';

export default {
  name: 'DishesView',
  components: {
    ReloadOutlined,
    PlusOutlined
  },
  data() {
    return {
      dishes: [],
      loading: false,
      dishDetailVisible: false,
      dishFormVisible: false,
      formLoading: false,
      selectedDish: null,
      currentDish: {},
      isEditing: false,
      columns: [
        {
          title: 'Name',
          dataIndex: 'name',
          key: 'name',
          sorter: (a, b) => a.name.localeCompare(b.name),
        },
        {
          title: 'Description',
          dataIndex: 'description',
          key: 'description',
          ellipsis: true,
        },
        {
          title: 'Category',
          dataIndex: 'category',
          key: 'category',
        },
        {
          title: 'Ingredients',
          dataIndex: 'ingredients',
          key: 'ingredients',
        },
        {
          title: 'Status',
          dataIndex: 'isAvailable',
          key: 'isAvailable',
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
        // Process ingredients from array to string for form
        this.dishes = response.data.map(dish => ({
          ...dish,
          ingredientsStr: Array.isArray(dish.ingredients) ? dish.ingredients.join(', ') : ''
        }));
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
        description: '',
        category: '',
        ingredientsStr: '',
        isAvailable: true,
        preparationTime: null,
        image: ''
      };
      this.isEditing = false;
      this.dishFormVisible = true;
    },
    editDish(dish) {
      this.currentDish = {
        ...dish,
        ingredientsStr: Array.isArray(dish.ingredients) ? dish.ingredients.join(', ') : ''
      };
      this.isEditing = true;
      this.dishFormVisible = true;
    },
    async saveDish() {
      this.formLoading = true;
      try {
        // Process ingredients from string to array
        const payload = {
          ...this.currentDish,
          ingredients: this.currentDish.ingredientsStr
            ? this.currentDish.ingredientsStr.split(',').map(ing => ing.trim()).filter(ing => ing)
            : []
        };

        // Remove the string version of ingredients
        delete payload.ingredientsStr;

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