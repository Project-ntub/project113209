<!-- src/components/backend/ChartModal.vue -->
<template>
  <div class="chart-modal-container">
    <div class="chart-modal">
      <div class="chart-modal-header">
        <!-- 顯示編輯或新增圖表的標題 -->
        <h2>{{ isEditing ? '編輯圖表' : '新增圖表' }}</h2>
        <!-- 關閉視窗的按鈕 -->
        <button @click="closeModal" class="close-btn">×</button>
      </div>
      <div class="chart-modal-body">
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

          <!-- Y 軸欄位選擇，當資料來源有欄位時顯示 -->
          <div class="setting" v-if="tableFields.length > 0">
            <label for="y-axis-field">Y 軸欄位</label>
            <select id="y-axis-field" v-model="chartData.yAxisField">
              <option v-for="field in tableFields" :key="field.name" :value="field.name">
                {{ field.verbose_name || field.name }}
              </option>
            </select>
          </div>

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
            </div>
          </div>

          <label for="threshold">數據標記閾值</label>
          <input id="threshold" v-model="chartData.threshold" type="number" placeholder="輸入閾值" />
        </div>
        <!-- 圖表預覽區域 -->
        <div class="chart-preview">
          <h3>預覽</h3>
          <PlotlyChart :chartConfig="chartData" />
        </div>
        <!-- 數據摘要顯示區域 -->
        <div class="chart-summary">
          <h3>數據摘要</h3>
          <p>{{ summary }}</p>
        </div>
      </div>
      <div class="chart-modal-footer">
        <!-- 保存或新增圖表的按鈕 -->
        <button class="btn-save" @click="saveChart">{{ isEditing ? '保存變更' : '新增圖表' }}</button>
        <!-- 取消操作的按鈕 -->
        <button class="btn-cancel" @click="closeModal">取消</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { Chrome } from '@ckpack/vue-color';
import PlotlyChart from '@/components/backend/PlotlyChart.vue';

// 引入不同類型的過濾組件
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
    DateFilter, 
    Chrome,
  },
  props: {
    isEditing: Boolean, // 判斷是否為編輯模式
    chartId: {
      type: Number,
      default: null // 圖表ID，若為新增則為 null
    },
    fetchChartConfig: {
      type: Function,
      required: true // 必須傳遞獲取圖表配置的方法
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
      summary: "",  // 數據摘要
      dataSource: [
        { value: 'TEST_Inventory', label: '庫存數據' },
        { value: 'TEST_Sales', label: '銷售數據' },
        { value: 'TEST_Revenue', label: '營業數據' },
        { value: 'TEST_Products', label: '商品數據' },
        // 添加更多資料來源
      ],
      tableFields: [], // 儲存選定資料來源的欄位
      filtersMetadata: [], // 儲存可用的過濾條件
      filterValues: {}, // 儲存用戶設置的過濾值


    };
  },
  mounted() {
    // 組件掛載後獲取資料來源
    this.fetchDataSources();
    if (this.isEditing && this.chartId) {
      // 如果是編輯模式，載入現有圖表配置
      this.loadChartConfig();
    }
  },
  watch: {
    // 監視資料來源的變化，並根據變化更新欄位和過濾條件
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
    // 監視 X 軸欄位的變化，並根據變化獲取圖表數據
    'chartData.xAxisField'(newVal) {
      if (newVal && this.chartData.yAxisField) {
        this.fetchChartData();
      }
    },
    // 監視 Y 軸欄位的變化，並根據變化獲取圖表數據
    'chartData.yAxisField'(newVal) {
      if (newVal && this.chartData.xAxisField) {
        this.fetchChartData();
      }
    },
    // 監視排序條件的變化，並根據變化獲取圖表數據
    'chartData.ordering'() {
      if (this.chartData.xAxisField && this.chartData.yAxisField) {
        this.fetchChartData();
      }
    },
    // 監視限制條件的變化，並根據變化獲取圖表數據
    'chartData.limit'() {
      if (this.chartData.xAxisField && this.chartData.yAxisField) {
        this.fetchChartData();
      }
    },
    // 監視過濾值的變化，並更新過濾條件
    filterValues: {
      handler() {
        this.updateFilterConditions();
      },
      deep: true // 深度監視對象內部變化
    }
  },
  methods: {
    fetchDataSources() {
      // 如果資料來源是動態的，請從後端獲取
      // 目前假設是靜態的，已在 data 中定義
    },
    async fetchTableFieldsMetadata() {
      // 獲取選定資料來源的欄位元數據
      try {
        const response = await axios.get(`/api/backend/table-fields-metadata/${this.chartData.dataSource}/`);
        this.tableFields = response.data.fields;
        // 根據欄位類型過濾出可用的過濾條件
        this.filtersMetadata = this.tableFields.filter(field => this.isFilterable(field));
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
      // 根據欄位類型選擇對應的過濾組件
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
      // 根據用戶設置的過濾值更新圖表的過濾條件
      const conditions = {};
      for (const [key, value] of Object.entries(this.filterValues)) {
        if (value === '' || (Array.isArray(value) && value.length === 0)) {
          continue; // 跳過空值
        }
        const filter = this.filtersMetadata.find(f => f.name === key);
        if (filter) {
          switch (filter.type) {
            case 'CharField':
            case 'TextField':
              conditions[key + '__icontains'] = value; // 模糊匹配
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
              // 根據實際情況修改外鍵的過濾條件
              if (key === 'product') {
                conditions['product__product_name__icontains'] = value;
              } else {
                conditions[key + '__name__icontains'] = value;
              }
              break;
            default:
              conditions[key] = value;
          }
        }
      }
      this.chartData.filterConditions = conditions;
      this.fetchChartData(); // 更新圖表數據
    },
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
      try {
        const response = await axios.get(`/api/backend/charts/${this.chartId}/`);
        const config = response.data;
        console.log('獲取到的圖表配置:', config); // 調試輸出

        this.chartData = {
          ...this.chartData,
          id: config.id,
          chartType: config.chartType,           // 使用駝峰命名
          name: config.name,
          dataSource: config.dataSource,         // 使用駝峰命名
          xAxisField: config.xAxisField,         // 使用駝峰命名
          yAxisField: config.yAxisField,         // 使用駝峰命名
          filterConditions: config.filter_conditions || {},
          ordering: config.ordering || [],
          limit: config.limit || null
        };
        console.log('更新後的 chartData:', this.chartData); // 調試輸出

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
          console.log('最終的 filterValues:', this.filterValues); // 調試輸出
          this.fetchChartData();
        }
      } catch (error) {
        console.error('獲取圖表配置出錯:', error);
        alert('獲取圖表配置時出錯，請檢查後端日誌以獲取更多信息。');
      }
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
  background: rgba(0, 0, 0, 0.5); /* 模態視窗背景色 */
  z-index: 1000; /* 確保模態視窗在最上層 */
  overflow-y: auto;
}

.chart-modal {
  background: #fff;
  padding: 20px;
  border-radius: 10px;
  width: 80%;
  max-width: 800px;
  max-height: 90vh; /* 限制最大高度 */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 模態視窗陰影 */
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
  background-color: #007BFF; /* 保存按鈕背景色 */
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
