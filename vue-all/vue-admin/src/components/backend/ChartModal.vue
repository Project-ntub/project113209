<template>
  <div class="chart-modal-container">
    <div class="chart-modal">
      <!-- Header -->
      <div class="chart-modal-header">
        <h2>{{ isEditing ? '編輯圖表' : '新增圖表' }}</h2>
        <button @click="closeModal" class="close-btn">×</button>
      </div>

      <!-- Body -->
      <div class="chart-modal-body">
<<<<<<< HEAD
        <div class="chart-settings">
          <!-- 圖表名稱設定 -->
          <div class="setting">
            <label for="chart-name">圖表名稱</label>
            <input id="chart-name" v-model="chartData.name" type="text" placeholder="輸入圖表名稱" />
          </div>
          <!-- 圖表類型選擇 -->
          <div class="setting">
            <label for="chart-type">圖表類型</label>
            <select id="chart-type" v-model="chartData.chartType">
              <option value="bar">柱狀圖</option>
              <option value="line">折線圖</option>
              <option value="pie">餅圖</option>
              <!-- <option value="heatmap">熱力圖</option> -->
              <option value="horizontal_bar">橫條圖</option>
              <option value="multi_line">多線折線圖</option>
              <option value="combo">組合式圖表</option>
              <!-- 更多圖表類型 -->
            </select>
          </div>
          <!-- 資料來源選擇 -->
          <div class="setting">
            <label for="data-source">資料來源</label>
            <select id="data-source" v-model="chartData.dataSource" @change="fetchTableFieldsMetadata">
              <option v-for="source in dataSource" :key="source.value" :value="source.value">
                {{ source.label }}
              </option>
            </select>
          </div>
          <!-- X 軸欄位選擇，當資料來源有欄位時顯示 -->
          <div class="setting" v-if="tableFields.length > 0">
            <label for="x-axis-field">X 軸欄位</label>
            <select id="x-axis-field" v-model="chartData.xAxisField">
              <option v-for="field in tableFields" :key="field.name" :value="field.name">
                {{ field.verbose_name || field.name }}
              </option>
            </select>
          </div>
=======
        <div class="chart-content-settings">
          <!-- Chart Settings -->
          <div class="chart-settings">
            <!-- Chart Name -->
            <div class="setting">
              <label for="chart-name">圖表名稱</label>
              <input id="chart-name" v-model="chartData.name" type="text" placeholder="輸入圖表名稱" />
            </div>
>>>>>>> ba0d8c41 (描述您的更改)

            <!-- Chart Type -->
            <div class="setting">
              <label for="chart-type">圖表類型</label>
              <select id="chart-type" v-model="chartData.chartType">
                <option value="bar">柱狀圖</option>
                <option value="line">折線圖</option>
                <option value="pie">餅圖</option>
              </select>
            </div>

<<<<<<< HEAD
          <!-- Y 軸欄位選擇，當資料來源有欄位時顯示 -->
          <div class="setting" v-if="chartData.chartType === 'multi_line' || chartData.chartType === 'combo'">
            <label for="y-axis-fields">Y 軸欄位（可多選）</label>
            <select id="y-axis-fields" v-model="chartData.yAxisFields" multiple>
              <option v-for="field in tableFields" :key="field.name" :value="field.name">
                {{ field.verbose_name || field.name }}
              </option>
            </select>
          </div>

          <label for="chart-color">圖表顏色</label>
          <!-- 使用顏色選擇器組件 -->
          <Chrome v-model="chartData.color" />

          <!-- 動態生成的過濾條件設定 -->
          <div class="filter-conditions" v-if="filtersMetadata.length > 0">
            <h3>過濾條件</h3>
            <div v-for="filter in filtersMetadata" :key="filter.name" class="filter-item">
              <label :for="'filter-' + filter.name">{{ filter.verbose_name || filter.name }}</label>
              <!-- 根據過濾條件的類型動態選擇組件 -->
              <component
                :is="getFilterComponent(filter)"
                :filter="filter"
                v-model="filterValues[filter.name]"
              />
=======
            <!-- Data Source -->
            <div class="setting">
              <label for="data-source">資料來源</label>
              <select id="data-source" v-model="chartData.dataSource" @change="fetchTableFieldsMetadata">
                <option v-for="source in dataSource" :key="source.value" :value="source.value">
                  {{ source.label }}
                </option>
              </select>
            </div>

            <!-- X Axis Field -->
            <div class="setting" v-if="tableFields.length > 0">
              <label for="x-axis-field">X 軸欄位</label>
              <select id="x-axis-field" v-model="chartData.xAxisField">
                <option v-for="field in tableFields" :key="field.name" :value="field.name">
                  {{ field.verbose_name || field.name }}
                </option>
              </select>
            </div>

            <!-- Y Axis Field -->
            <div class="setting" v-if="tableFields.length > 0">
              <label for="y-axis-field">Y 軸欄位</label>
              <select id="y-axis-field" v-model="chartData.yAxisField">
                <option v-for="field in tableFields" :key="field.name" :value="field.name">
                  {{ field.verbose_name || field.name }}
                </option>
              </select>
            </div>

            <!-- Filters -->
            <div class="filter-conditions" v-if="filtersMetadata.length > 0">
              <h3>過濾條件</h3>
              <div v-for="filter in filtersMetadata" :key="filter.name" class="filter-item">
                <label :for="'filter-' + filter.name">{{ filter.verbose_name || filter.name }}</label>
                <component :is="getFilterComponent(filter)" :filter="filter" v-model="filterValues[filter.name]" />
              </div>
            </div>

            <!-- Chart Summary -->
            <div class="chart-summary">
              <h3>數據摘要</h3>
              <p>{{ summary }}</p>
>>>>>>> ba0d8c41 (描述您的更改)
            </div>
          </div>

          <label for="threshold">數據標記閾值</label>
          <input id="threshold" v-model="chartData.threshold" type="number" placeholder="輸入閾值" />
        </div>
      </div>

      <!-- Footer -->
      <div class="chart-modal-footer">
        <div class="footer-left">
          <button class="btn-save" @click="saveChart">{{ isEditing ? '保存變更' : '新增圖表' }}</button>
          <button class="btn-cancel" @click="closeModal">取消</button>
        </div>
      </div>
    </div>

    <!-- Chart Preview (Separate Interface) -->
    <div class="chart-preview-container">
      <div class="chart-preview">
        <h3>預覽</h3>
        <PlotlyChart :chartConfig="chartData" />
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Chrome } from '@ckpack/vue-color';
import PlotlyChart from '@/components/backend/PlotlyChart.vue';
import TextFilter from '@/components/backend/filters/TextFilter.vue';
import SelectFilter from '@/components/backend/filters/SelectFilter.vue';
import CheckboxFilter from '@/components/backend/filters/CheckboxFilter.vue';
import NumberFilter from '@/components/backend/filters/NumberFilter.vue';
import DateFilter from '@/components/backend/filters/DateFilter.vue';

export default {
  components: {
    PlotlyChart,
    TextFilter,
    SelectFilter,
    CheckboxFilter,
    NumberFilter,
    DateFilter, 
    Chrome,
  },
  props: {
    isEditing: Boolean,
    chartId: {
      type: Number,
      default: null
    },
    fetchChartConfig: {
      type: Function,
      required: true
    }
  },
  data() {
    return {
      chartData: {
        id: null,
        chartType: 'bar',
        name: '',
        dataSource: '',
        xAxisField: '',
        yAxisField: '',
        filterConditions: {},
        ordering: [],
        limit: null,
        x_data: [],
        y_data: [],
        joinFields: [],
        yAxisFields: [],
        color: {
          hex: '#000000',
        },       
        threshold: null, // 閾值
      },
      summary: "",
      dataSource: [
        { value: 'TEST_Inventory', label: '庫存數據' },
        { value: 'TEST_Sales', label: '銷售數據' },
        { value: 'TEST_Revenue', label: '營業數據' },
        { value: 'TEST_Products', label: '商品數據' }
      ],
<<<<<<< HEAD
      tableFields: [], // 儲存選定資料來源的欄位
      filtersMetadata: [], // 儲存可用的過濾條件
      filterValues: {}, // 儲存用戶設置的過濾值


=======
      tableFields: [],
      filtersMetadata: [],
      filterValues: {}
>>>>>>> ba0d8c41 (描述您的更改)
    };
  },
  mounted() {
    this.fetchDataSources();
    if (this.isEditing && this.chartId) {
      this.loadChartConfig();
    }
  },
  watch: {
    'chartData.dataSource'(newSource) {
      if (newSource) {
        this.fetchTableFieldsMetadata();
        this.filterValues = {};
        this.chartData.filterConditions = {};
      } else {
        this.tableFields = [];
        this.filtersMetadata = [];
        this.filterValues = {};
        this.chartData.filterConditions = {};
      }
    },
    'chartData.xAxisField'(newVal) {
      if (newVal && this.chartData.yAxisField) {
        this.fetchChartData();
      }
    },
    'chartData.yAxisField'(newVal) {
      if (newVal && this.chartData.xAxisField) {
        this.fetchChartData();
      }
    },
    'chartData.ordering'() {
      if (this.chartData.xAxisField && this.chartData.yAxisField) {
        this.fetchChartData();
      }
    },
    'chartData.limit'() {
      if (this.chartData.xAxisField && this.chartData.yAxisField) {
        this.fetchChartData();
      }
    },
    filterValues: {
      handler() {
        this.updateFilterConditions();
      },
      deep: true
    }
  },
  methods: {
    fetchDataSources() {
      // For dynamic data sources, fetch from backend; here it's hardcoded
    },
    async fetchTableFieldsMetadata() {
      try {
        const response = await axios.get(`/api/backend/table-fields-metadata/${this.chartData.dataSource}/`);
        this.tableFields = response.data.fields;
        this.filtersMetadata = this.tableFields.filter(field => this.isFilterable(field));
        this.filterValues = {};
        this.filtersMetadata.forEach(filter => {
          this.filterValues[filter.name] = this.getDefaultFilterValue(filter);
        });
      } catch (error) {
        console.error('獲取欄位元數據出錯:', error);
        alert('獲取欄位元數據時出錯，請檢查後端日誌。');
      }
    },
    async fetchChartData() {
      if (!this.chartData.dataSource || !this.chartData.xAxisField || !this.chartData.yAxisField) {
        console.error('dataSource, xAxisField, 和 yAxisField 必須設置');
        return;
      }
      try {
        const response = await axios.post('/api/backend/dynamic-chart-data/', {
          table_name: this.chartData.dataSource,
          x_field: this.chartData.xAxisField,
          y_field: this.chartData.yAxisField,
          filter_conditions: this.chartData.filterConditions,
          ordering: this.chartData.ordering,
          limit: this.chartData.limit
        });

        const { x_data, y_data, last_updated } = response.data;
        if (x_data && y_data) {
          this.chartData.x_data = x_data;
          this.chartData.y_data = y_data;
          this.chartData.last_updated = last_updated;
          await this.fetchChartSummary();
        } else {
          console.error('x_data 和 y_data 不能為空');
        }
      } catch (error) {
        console.error('獲取圖表數據時出錯:', error);
        alert('獲取圖表數據時出錯，請檢查後端日誌。');
      }
    },
    async loadChartConfig() {
      try {
        const response = await axios.get(`/api/backend/charts/${this.chartId}/`);
        const config = response.data;

        this.chartData = {
          ...this.chartData,
          id: config.id,
          chartType: config.chartType,
          name: config.name,
          dataSource: config.dataSource,
          xAxisField: config.xAxisField,
          yAxisField: config.yAxisField,
          filterConditions: config.filter_conditions || {},
          ordering: config.ordering || [],
          limit: config.limit || null
        };

        if (this.chartData.dataSource) {
          await this.fetchTableFieldsMetadata();
          this.filtersMetadata.forEach(filter => {
            this.filterValues[filter.name] = this.getDefaultFilterValue(filter);
          });
          this.fetchChartData();
        }
      } catch (error) {
        console.error('獲取圖表配置出錯:', error);
        alert('獲取圖表配置時出錯，請檢查後端日誌以獲取更多信息。');
      }
    },
    saveChart() {
      if (!this.chartData.dataSource || !this.chartData.xAxisField || !this.chartData.yAxisField) {
        alert('資料來源、X 軸欄位和 Y 軸欄位是必填的。');
        return;
      }

      let chartConfig = {
        chart_type: this.chartData.chartType,
        name: this.chartData.name || '未命名圖表',
        data_source: this.chartData.dataSource,
        x_axis_field: this.chartData.xAxisField,
        y_axis_field: this.chartData.yAxisField,
        filter_conditions: this.chartData.filterConditions,
        ordering: this.chartData.ordering,
        limit: this.chartData.limit
      };

      if (this.isEditing) {
        axios.post(`/api/backend/update-chart/${this.chartId}/`, chartConfig)
          .then(async () => {
            alert('圖表已成功更新！');
            await this.$store.dispatch('fetchPermissions');
            this.$emit('reload-charts');
            this.closeModal();
          })
          .catch(error => {
            const errorMsg = error.response?.data?.error || '發生未知錯誤';
            alert(`更新圖表失敗: ${errorMsg}`);
          });
      } else {
        axios.post('/api/backend/create-chart/', chartConfig)
          .then(() => {
            alert('圖表已成功創建！');
            this.$emit('reload-charts');
            this.closeModal();
          })
          .catch(error => {
            const errorMsg = error.response?.data?.error || '發生未知錯誤';
            alert(`創建圖表失敗: ${errorMsg}`);
          });
      }
    },
    closeModal() {
      this.$emit('close');
    },
    isFilterable(field) {
      const filterableTypes = ['CharField', 'TextField', 'IntegerField', 'FloatField', 'DateTimeField', 'DateField', 'ForeignKey'];
      return filterableTypes.includes(field.type);
    },
    getFilterComponent(filter) {
      switch (filter.type) {
        case 'CharField':
        case 'TextField':
          return 'TextFilter';
        case 'IntegerField':
        case 'FloatField':
          return 'NumberFilter';
        case 'DateTimeField':
        case 'DateField':
          return 'DateFilter';
        case 'ForeignKey':
          return 'SelectFilter';
        default:
          return 'TextFilter';
      }
    },
    getDefaultFilterValue(filter) {
      switch (filter.type) {
        case 'CharField':
        case 'TextField':
          return '';
        case 'IntegerField':
        case 'FloatField':
          return { min: '', max: '' };
        case 'DateTimeField':
        case 'DateField':
          return { start: '', end: '' };
        case 'ForeignKey':
          return '';
        default:
          return '';
      }
    },
    updateFilterConditions() {
      const conditions = {};
      for (const [key, value] of Object.entries(this.filterValues)) {
        if (value === '' || (Array.isArray(value) && value.length === 0)) continue;

        const filter = this.filtersMetadata.find(f => f.name === key);
        if (filter) {
          switch (filter.type) {
            case 'CharField':
            case 'TextField':
              conditions[key + '__icontains'] = value;
              break;
            case 'IntegerField':
            case 'FloatField':
              if (value.min !== '' && value.max !== '') {
                conditions[key + '__range'] = [value.min, value.max];
              } else if (value.min !== '') {
                conditions[key + '__gte'] = value.min;
              } else if (value.max !== '') {
                conditions[key + '__lte'] = value.max;
              }
              break;
            case 'DateTimeField':
            case 'DateField':
              if (value.start && value.end) {
                conditions[key + '__range'] = [value.start, value.end];
              } else if (value.start) {
                conditions[key + '__gte'] = value.start;
              } else if (value.end) {
                conditions[key + '__lte'] = value.end;
              }
              break;
            case 'ForeignKey':
              conditions[key + '__name__icontains'] = value;
              break;
            default:
              conditions[key] = value;
          }
        }
      }
      this.chartData.filterConditions = conditions;
      this.fetchChartData();
    },
<<<<<<< HEAD
    async fetchChartData() { // 標記為 async
      // 獲取圖表數據的函數
      if (!this.chartData.dataSource || !this.chartData.xAxisField || !this.chartData.yAxisField) {
        console.error('dataSource, xAxisField, 和 yAxisField 必須設置');
        return;
      }
      try {
        // 發送請求到後端獲取動態圖表數據
        const response = await axios.post('/api/backend/dynamic-chart-data/', {
          table_name: this.chartData.dataSource,
          x_field: this.chartData.xAxisField,
          y_field: this.chartData.chartType === 'multi_line' ? null : this.chartData.yAxisField,
          y_fields: this.chartData.chartType === 'multi_line' ? this.chartData.yAxisFields : null,
          filter_conditions: this.chartData.filterConditions,
          chart_type: this.chartData.chartType,
          ordering: this.chartData.ordering,
          limit: this.chartData.limit
        });
        const { x_data, y_data, last_updated } = response.data;
        this.chartData.last_updated = last_updated;

        if (this.chartData.chartType === 'multi_line') {
          this.chartData.x_data = x_data;
          this.chartData.y_data = y_data; // y_data 是一個對象，鍵為 y_field 名稱
        } else {
          this.chartData.x_data = x_data;
          this.chartData.y_data = y_data;
        }
      } catch (error) {
        console.error('獲取圖表數據時出錯:', error);
        alert('獲取圖表數據時出錯，請檢查後端日誌。');
      }
    },
    async loadChartConfig() { // 標記為 async
      // 加載現有圖表配置的函數
=======
    async fetchChartSummary() {
>>>>>>> ba0d8c41 (描述您的更改)
      try {
        const response = await axios.post('/api/backend/chart-summary/', {
          table_name: this.chartData.dataSource,
          x_field: this.chartData.xAxisField,
          y_field: this.chartData.yAxisField,
          filter_conditions: this.chartData.filterConditions
        });
        this.summary = response.data.summary;
      } catch (error) {
        console.error('獲取數據摘要時出錯:', error);
      }
<<<<<<< HEAD
    },
    saveChart() {
      // 保存或新增圖表的函數
      // 檢查必要字段是否已填寫
      if (!this.chartData.dataSource || !this.chartData.xAxisField || !this.chartData.yAxisField) {
        alert('資料來源、X 軸欄位和 Y 軸欄位是必填的。');
        return;
      }

      // 組裝圖表配置數據
      let chartConfig = {
        chart_type: this.chartData.chartType,
        name: this.chartData.name || '未命名圖表',
        data_source: this.chartData.dataSource,
        x_axis_field: this.chartData.xAxisField,
        y_axis_field: this.chartData.yAxisField,
        filter_conditions: this.chartData.filterConditions,
        ordering: this.chartData.ordering,
        limit: this.chartData.limit,
        color: this.chartData.color,
      };

      if (this.isEditing) {
        // 如果是編輯模式，發送更新請求
        axios.post(`/api/backend/update-chart/${this.chartId}/`, chartConfig)
          .then(async () => {
            alert('圖表已成功更新！');
            await this.$store.dispatch('fetchPermissions'); // 刷新權限
            this.$emit('reload-charts');
            this.closeModal();
          })
          .catch(error => {
            const errorMsg = error.response?.data?.error || '發生未知錯誤';
            alert(`更新圖表失敗: ${errorMsg}`);
          });
      } else {
        // 如果是新增模式，發送創建請求
        axios.post('/api/backend/create-chart/', chartConfig)
          .then(() => {
            alert('圖表已成功創建！');
            this.$emit('reload-charts'); // 發出重新載入圖表的事件
            this.closeModal();
          })
          .catch(error => {
            const errorMsg = error.response?.data?.error || '發生未知錯誤';
            alert(`創建圖表失敗: ${errorMsg}`);
          });
      }
    },
    closeModal() {
      // 關閉模態視窗的函數
      this.$emit('close');

    
=======
>>>>>>> ba0d8c41 (描述您的更改)
    }
  }
};
</script>

<style scoped>
.chart-modal-container {
  display: flex;
  flex-direction: row; /* 讓設定視窗在左邊，預覽視窗在右邊 */
  justify-content: flex-start;
  align-items: flex-start;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  backdrop-filter: blur(5px);
  background: rgba(0, 0, 0, 0.4);
  z-index: 1000;
  overflow-y: auto;
  gap: 40px; /* 調整間距，讓兩個視窗之間有適當的空間 */
  padding-left: 200px; /* 確保左邊的設定窗口有空間 */
  margin-left: 50px; /* 將整個容器右移 */
}

.chart-modal {
  background: #ffffff;
  padding: 10px;
  border-radius: 8px;
  width: 30%;
  max-width: 450px;
  max-height: 80vh;
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.2);
  overflow-y: auto;
  animation: fadeIn 0.3s ease-in-out;
}

.chart-preview-container {
  background: #ffffff;
  padding: 10px;
  border-radius: 8px;
  width: 40%;
  max-width: 600px;
  max-height: 80vh;
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.2);
  overflow-y: auto;
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chart-modal-header,
.chart-modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.chart-modal-header h2 {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
}

.chart-modal-header .close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #666;
  cursor: pointer;
  transition: color 0.3s;
}

.chart-modal-header .close-btn:hover {
  color: #ff4d4f;
}

.chart-modal-body {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chart-content-settings {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.chart-settings {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  background: #f9f9f9;
}

.chart-summary {
  margin-top: 10px;
  border: 1px solid #eee;
  padding: 8px;
  border-radius: 6px;
  background: #f9f9f9;
}

.chart-preview {
  border: 1px solid #ccc;
  padding: 10px;
  border-radius: 6px;
  height: 100%;
  background: #fafafa;
}

.footer-left {
  display: flex;
  gap: 8px;
}

.btn-save {
  background: linear-gradient(90deg, #007BFF, #0056b3);
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 15px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s;
}

.btn-save:hover {
  background: linear-gradient(90deg, #0056b3, #003f7f);
}

.btn-cancel {
  background: none;
  color: #333;
  border: 2px solid #ddd;
  padding: 6px 12px;
  border-radius: 15px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background 0.3s, color 0.3s;
}

.btn-cancel:hover {
  background: #f8f9fa;
  color: #007BFF;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
</style>
