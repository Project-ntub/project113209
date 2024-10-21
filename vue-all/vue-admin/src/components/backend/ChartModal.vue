<!-- src/components/backend/ChartModal.vue -->
<template>
  <div class="chart-modal-container">
    <div class="chart-modal">
      <div class="chart-modal-header">
        <h2>{{ isEditing ? '編輯圖表' : '新增圖表' }}</h2>
        <button @click="closeModal" class="close-btn">×</button>
      </div>
      <div class="chart-modal-body">
        <div class="chart-settings">
          <!-- 圖表名稱 -->
          <div class="setting">
            <label for="chart-name">圖表名稱</label>
            <input id="chart-name" v-model="chartData.name" type="text" placeholder="輸入圖表名稱" />
          </div>
          <!-- 圖表類型 -->
          <div class="setting">
            <label for="chart-type">圖表類型</label>
            <select id="chart-type" v-model="chartData.chartType">
              <option value="bar">柱狀圖</option>
              <option value="line">折線圖</option>
              <option value="pie">餅圖</option>
              <!-- 更多圖表類型 -->
            </select>
          </div>
          <!-- 資料來源 -->
          <div class="setting">
            <label for="data-source">資料來源</label>
            <select id="data-source" v-model="chartData.dataSource" @change="fetchTableFieldsMetadata">
              <option v-for="source in dataSource" :key="source.value" :value="source.value">
                {{ source.label }}
              </option>
            </select>
          </div>
          <!-- X 軸欄位選擇 -->
          <div class="setting" v-if="tableFields.length > 0">
            <label for="x-axis-field">X 軸欄位</label>
            <select id="x-axis-field" v-model="chartData.xAxisField">
              <option v-for="field in tableFields" :key="field.name" :value="field.name">
                {{ field.verbose_name || field.name }}
              </option>
            </select>
          </div>

          <!-- Y 軸欄位選擇 -->
          <div class="setting" v-if="tableFields.length > 0">
            <label for="y-axis-field">Y 軸欄位</label>
            <select id="y-axis-field" v-model="chartData.yAxisField">
              <option v-for="field in tableFields" :key="field.name" :value="field.name">
                {{ field.verbose_name || field.name }}
              </option>
            </select>
          </div>

          <!-- 動態生成的過濾條件 -->
          <div class="filter-conditions" v-if="filtersMetadata.length > 0">
            <h3>過濾條件</h3>
            <div v-for="filter in filtersMetadata" :key="filter.name" class="filter-item">
              <label :for="'filter-' + filter.name">{{ filter.verbose_name || filter.name }}</label>
              <component
                :is="getFilterComponent(filter)"
                :filter="filter"
                v-model="filterValues[filter.name]"
              />
            </div>
          </div>
        </div>
        <!-- 圖表預覽 -->
        <div class="chart-preview">
          <h3>預覽</h3>
          <PlotlyChart :chartConfig="chartData" />
        </div>
      </div>
      <div class="chart-modal-footer">
        <button class="btn-save" @click="saveChart">{{ isEditing ? '保存變更' : '新增圖表' }}</button>
        <button class="btn-cancel" @click="closeModal">取消</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import PlotlyChart from '@/components/backend/PlotlyChart.vue';

// 引入過濾組件
import TextFilter from '@/components/backend/filters/TextFilter.vue';
import SelectFilter from '@/components/backend/filters/SelectFilter.vue';
import CheckboxFilter from '@/components/backend/filters/CheckboxFilter.vue';
import NumberFilter from '@/components/backend/filters/NumberFilter.vue'; // 假設已創建
import DateFilter from '@/components/backend/filters/DateFilter.vue'; // 假設已創建

export default {
  components: {
    PlotlyChart,
    TextFilter,
    SelectFilter,
    CheckboxFilter,
    NumberFilter,
    DateFilter
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
        joinFields: []
      },
      dataSource: [
        { value: 'TEST_Inventory', label: '庫存數據' },
        { value: 'TEST_Sales', label: '銷售數據' },
        { value: 'TEST_Revenue', label: '營業數據' },
        { value: 'TEST_Products', label: '商品數據' },
        // 添加更多資料來源
      ],
      tableFields: [],
      filtersMetadata: [],
      filterValues: {}
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
        // 重置過濾條件
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
      // 如果資料來源是動態的，請從後端獲取
      // 目前假設是靜態的，已在 data 中定義
    },
    async fetchTableFieldsMetadata() { // 標記為 async
      try {
        const response = await axios.get(`/api/backend/table-fields-metadata/${this.chartData.dataSource}/`);
        this.tableFields = response.data.fields;
        this.filtersMetadata = response.data.fields.filter(field => this.isFilterable(field));
        // 重置過濾條件
        this.filterValues = {};
        this.chartData.filterConditions = {};
        // 初始化 filterValues
        this.filtersMetadata.forEach(filter => {
          this.filterValues[filter.name] = this.getDefaultFilterValue(filter);
        });
      } catch (error) {
        console.error('獲取欄位元數據出錯:', error);
        alert('獲取欄位元數據時出錯，請檢查後端日誌。');
      }
    },
    isFilterable(field) {
      // 定義哪些欄位可以過濾，根據需要調整
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
      // 根據過濾類型設置默認值
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
        if (value === '' || (Array.isArray(value) && value.length === 0)) {
          continue;
        }
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
              // **修正此處，使用正確的字段名稱**
              // 例如，對於 `product` 外鍵，應使用 `product__product_name__icontains`
              if (key === 'product') {
                conditions['product__product_name__icontains'] = value;
              } else {
                // 其他外鍵處理
                conditions[key + '__name__icontains'] = value; // 根據實際情況修改
              }
              break;
            default:
              conditions[key] = value;
          }
        }
      }
      this.chartData.filterConditions = conditions;
      this.fetchChartData();
    },
    async fetchChartData() { // 標記為 async
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
        } else {
          console.error('x_data 和 y_data 不能為空');
        }
      } catch (error) {
        console.error('獲取圖表數據時出錯:', error);
        alert('獲取圖表數據時出錯，請檢查後端日誌。');
      }
    },
    async loadChartConfig() { // 標記為 async
      try {
        const response = await axios.get(`/api/backend/charts/${this.chartId}/`);
        const config = response.data;
        console.log('Fetched chart config:', config); // 調試輸出

        this.chartData = {
          ...this.chartData,
          id: config.id,
          chartType: config.chartType,           // 使用駝峰式
          name: config.name,
          dataSource: config.dataSource,         // 使用駝峰式
          xAxisField: config.xAxisField,         // 使用駝峰式
          yAxisField: config.yAxisField,         // 使用駝峰式
          filterConditions: config.filter_conditions || {},
          ordering: config.ordering || [],
          limit: config.limit || null
        };
        console.log('Updated chartData:', this.chartData); // 調試輸出

        if (this.chartData.dataSource) {
          await this.fetchTableFieldsMetadata();
          // 設置過濾值
          this.filtersMetadata.forEach(filter => {
            this.filterValues[filter.name] = this.getDefaultFilterValue(filter);
          });
          // 根據 config.filter_conditions 設置 filterValues
          for (const [key, value] of Object.entries(this.chartData.filterConditions)) {
            const baseKey = key.split('__')[0]; // 取得基本字段名
            const filter = this.filtersMetadata.find(f => f.name === baseKey);
            if (filter) {
              if (key.includes('__range')) {
                this.filterValues[filter.name] = { min: value[0], max: value[1] };
              } else if (key.includes('__gte')) {
                this.filterValues[filter.name] = { ...this.filterValues[filter.name], min: value };
              } else if (key.includes('__lte')) {
                this.filterValues[filter.name] = { ...this.filterValues[filter.name], max: value };
              } else {
                this.filterValues[filter.name] = value;
              }
            }
          }
          console.log('Final filterValues:', this.filterValues); // 調試輸出
          this.fetchChartData();
        }
      } catch (error) {
        console.error('獲取圖表配置出錯:', error);
        alert('獲取圖表配置時出錯，請檢查後端日誌以獲取更多信息。');
      }
    },
    saveChart() {
      // 檢查必要字段
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
            await this.$store.dispatch('fetchPermissions'); // 刷新權限
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
            this.$emit('reload-charts'); // 發出事件
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
    }
  }
};
</script>

<style scoped>
.chart-modal-container {
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  overflow-y: auto;
}

.chart-modal {
  background: #fff;
  padding: 20px;
  border-radius: 10px;
  width: 80%;
  max-width: 800px;
  max-height: 90vh; /* 限制最大高度 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
}

.chart-modal-header,
.chart-modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-modal-body {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-settings {
  flex: 1;
}

.chart-preview {
  flex: 1;
  border: 1px solid #ccc;
  padding: 10px;
  height: 500px;
  width: 100%;
}

.setting {
  margin-bottom: 15px;
}

.btn-save,
.btn-cancel {
  background-color: #007BFF;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.filter-item {
  margin-bottom: 10px;
}
</style>
