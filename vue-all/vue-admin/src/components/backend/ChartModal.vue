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
              <option value="bar">直條圖</option>
              <option value="line">折線圖</option>
              <option value="pie">餅圖</option>
              <!-- <option value="grouped_bar">分組條形圖</option>
              <option value="stacked_bar">堆疊條形圖</option>
              <option value="area">區域圖</option>
              <option value="scatter">散點圖</option> -->
              <option value="horizontal_bar">橫條圖</option>
              <option value="multi_line">多線折線圖</option>
              <option value="combo">組合式圖表</option>
              <option value="donut">環型圖</option>
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

          <!-- 單一 Y 軸欄選擇，當圖表類型不是 'multi_line' 或 'combo' 時顯示-->
          <div class="setting" v-if="tableFields.length > 0 && chartData.chartType !== 'multi_line' && chartData.chartType !== 'combo'">
            <label for="y-axis-field">Y 軸欄位</label>
            <select id="y-axis-field" v-model="chartData.yAxisField">
              <option v-for="field in tableFields" :key="field.name" :value="field.name">
                {{ field.verbose_name || field.name }}
              </option>
            </select>
          </div>

          <!-- 多個 Y 軸欄位選擇 -->
          <div class="setting" v-if="['multi_line', 'combo', 'stacked_bar', 'grouped_bar'].includes(chartData.chartType)">            <label for="y-axis-fields">Y 軸欄位（可多重選擇，至少選兩個）</label>
            <multiselect
              id="y-axis-fields"
              v-model="chartData.yAxisFields"
              :options="tableFields"
              :multiple="true"
              :close-on-select="false"
              :clear-on-select="false"
              :preserve-search="true"
              :preselect-first="false"
              label="verbose_name"
              track-by="name"
              placeholder="請選擇 Y 軸欄位"
            ></multiselect>
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
import Multiselect from 'vue-multiselect';

// 引入不同類型的過濾組件
import TextFilter from '@/components/backend/filters/TextFilter.vue';
import SelectFilter from '@/components/backend/filters/SelectFilter.vue';
import CheckboxFilter from '@/components/backend/filters/CheckboxFilter.vue';
import NumberFilter from '@/components/backend/filters/NumberFilter.vue';
import DateFilter from '@/components/backend/filters/DateFilter.vue';
import { fetchChartData } from '@/utils/chartDataProcessor';


export default {
  components: {
    PlotlyChart,
    TextFilter,
    SelectFilter,
    CheckboxFilter,
    NumberFilter,
    DateFilter,
    Chrome,
    Multiselect,
  },
  props: {
    isEditing: Boolean,
    chartId: {
      type: Number,
      default: null, // 圖表ID，若為新增則為 null
    },
    fetchChartConfig: {
      type: Function,
      required: true, // 必須傳遞獲取圖表配置的方法
    },
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
        labels: [],     // 用於 treemap、donut、funnel
        values: [],     // 用於 treemap、donut、funnel
        parents: [],    // 用於 treemap
        color: {
          hex: '#000000',
        },
        threshold: null, // 閾值
      },
      summary: '', // 數據摘要
      dataSource: [
        { value: 'TEST_Inventory', label: '庫存數據' },
        { value: 'TEST_Sales', label: '銷售數據' },
        { value: 'TEST_Revenue', label: '營業數據' },
        { value: 'TEST_Products', label: '商品數據' }
      ],
      tableFields: [], // 儲存選定資料來源的欄位
      filtersMetadata: [], // 儲存可用的過濾條件
      filterValues: {}, // 儲存用戶設置的過濾值
      isLoadingConfig: false,
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
      if (
        newVal &&
        this.chartData.xAxisField &&
        this.chartData.chartType !== 'multi_line' &&
        this.chartData.chartType !== 'combo'
      ) {
        this.fetchChartData();
      }
    },
    'chartData.yAxisFields': {
      handler(newVal) {
        if (
          !this.isLoadingConfig && // 確保不是在在入配置時
          newVal &&
          newVal.length >= 2 &&
          this.chartData.xAxisField &&
          (this.chartData.chartType === 'multi_line' || this.chartData.chartType === 'combo')
        ) {
          this.fetchChartData();
        }
      },
      deep: true,
    },
    // 監視排序條件的變化，並根據變化獲取圖表數據
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
      deep: true, // 深度監視對象內部變化
    },
  },
  methods: {
    fetchDataSources() {
      // For dynamic data sources, fetch from backend; here it's hardcoded
    },
    async fetchTableFieldsMetadata() {
      return new Promise(async (resolve, reject) => {
        try {
          const response = await axios.get(`/api/backend/table-fields-metadata/${this.chartData.dataSource}/`);
          this.tableFields = response.data.fields;
          console.log('獲取到的 tableFields:', this.tableFields.map(field => field.name));
          // 根據欄位類型過濾出可用的過濾條件
          this.filtersMetadata = this.tableFields.filter(field => this.isFilterable(field));
          // 重置過濾條件
          this.filterValues = {};
          this.chartData.filterConditions = {};
          // 初始化 filterValues
          this.filtersMetadata.forEach(filter => {
            this.filterValues[filter.name] = this.getDefaultFilterValue(filter);
          });
          resolve();
        } catch (error) {
          console.error('獲取欄位元數據出錯:', error);
          alert('獲取欄位元數據時出錯，請檢查後端日誌。');
          reject(error);
        }
      });
    },
    async fetchChartSummary() {
      try {
        const response = await axios.post('/api/backend/chart-summary/', {
          table_name: this.chartData.dataSource,
          x_field: this.chartData.xAxisField,
          y_field: this.chartData.yAxisField,
          filter_conditions: this.chartData.filterConditions,
        });
        this.summary = response.data.summary;
      } catch (error) {
        console.error('獲取數據摘要時出錯:', error);
      }
    },
    isFilterable(field) {
      // 定義哪些欄位可以過濾，根據需要調整
      const filterableTypes = [
        'CharField',
        'TextField',
        'IntegerField',
        'FloatField',
        'DateTimeField',
        'DateField',
        'ForeignKey',
      ];
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
    async fetchChartData() {
      try {
        const requestData = {
          table_name: this.chartData.dataSource,
          x_field: this.chartData.xAxisField,
          chart_type: this.chartData.chartType,
          filter_conditions: this.chartData.filterConditions,
          ordering: this.chartData.ordering,
          limit: this.chartData.limit
        };

        if (this.chartData.chartType === 'multi_line' || this.chartData.chartType === 'combo') {
          // 將 yAxisFields (物件陣列) 轉換為字串陣列
          requestData.y_fields = this.chartData.yAxisFields.map(field => field.name);
        } else {
          requestData.y_field = this.chartData.yAxisField;
        }
        console.log('發送的請求數據:', this.chartData);
        const data = await fetchChartData(this.chartData);
        console.log('收到的數據:', data);

        // 根據圖表類型處理數據
        switch (this.chartData.chartType) {
          // case 'treemap':
          //   this.chartData.x_data = data.labels || [];
          //   this.chartData.y_data = data.values || [];
          //   this.chartData.parents = data.parents || [];
          //   break;
          case 'donut':
            this.chartData.x_data = data.labels || data.x_data || [];
            this.chartData.y_data = data.values || data.y_data || [];
            if (this.chartData.chartType === 'treemap') {
                this.chartData.parents = data.parents || [];
            }
            console.log('Processed chart data:', {
                labels: this.chartData.labels,
                values: this.chartData.values,
                parents: this.chartData.parents
            });
            break;
          // case 'funnel':
          //   this.chartData.x_data = data.labels || [];
          //   this.chartData.y_data = data.values || [];
          //   break;
          case 'multi_line':
            this.chartData.x_data = data.x_data || [];
            this.chartData.y_data = data.y_data || {};
            break;
          case 'combo':
            this.chartData.x_data = data.x_data || [];
            this.chartData.y_data_bar = data.y_data_bar || [];
            this.chartData.y_data_line = data.y_data_line || [];
            break;
          default:
            this.chartData.x_data = data.x_data || [];
            this.chartData.y_data = data.y_data || [];
        }
      } catch (error) {
        console.error('獲取圖表數據時出錯:', error);
      }
    },
    async loadChartConfig() {
      this.isLoadingConfig = true;  // 開始載入配置
      // 加載現有圖表配置的函數
      try {
        const response = await axios.get(`/api/backend/charts/${this.chartId}/`);
        const config = response.data;
        console.log('獲取到的圖表配置:', config); // 調試輸出

        this.chartData = {
          ...this.chartData,
          id: config.id,
          chartType: config.chartType, // 使用駝峰命名
          name: config.name,
          dataSource: config.dataSource, // 使用駝峰命名
          xAxisField: config.xAxisField, // 使用駝峰命名
          yAxisField: config.yAxisField, // 使用駝峰命名
          yAxisFields: config.yAxisFields || [],
          filterConditions: config.filterConditions || {},
          ordering: config.ordering || [],
          limit: config.limit || null,
          color: config.color ? { hex: config.color } : { hex: '#000000' }
        };
        console.log('更新後的 chartData:', this.chartData); // 調試輸出

        if (this.chartData.dataSource) {
          // 確保 fetchTableFieldsMetadata 已完成
          await this.fetchTableFieldsMetadata();
          // 等待 DOM 和資料更新完成
          await this.$nextTick();

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

          // **將欄位匹配的代碼移到這裡**
          console.log('原始的 yAxisFields:', this.chartData.yAxisFields);
          console.log('獲取到的 tableFields:', this.tableFields.map(field => field.name));

          if (this.chartData.yAxisFields && Array.isArray(this.chartData.yAxisFields)) {
            if (typeof this.chartData.yAxisFields[0] === 'string') {
              const yAxisFieldsLower = this.chartData.yAxisFields.map(field => field.toLowerCase());
              this.chartData.yAxisFields = this.tableFields.filter(field =>
                yAxisFieldsLower.includes(field.name.toLowerCase()),
              );
            }
          } else {
            this.chartData.yAxisFields = [];
          }

          console.log('處理後的 yAxisFields:', this.chartData.yAxisFields);

          this.fetchChartData();
        }
      } catch (error) {
        console.error('獲取圖表配置出錯:', error);
        alert('獲取圖表配置時出錯，請檢查後端日誌以獲取更多信息。');
      } finally {
        this.isLoadingConfig = false; // 載入完成
      }
    },
    saveChart() {
      // 保存或新增圖表的函數
      // 檢查必要字段是否已填寫
      if (!this.chartData.dataSource || !this.chartData.xAxisField) {
        alert('資料來源和 X 軸欄位是必填的。');
        return;
      }

      // 對於不同的圖表類型，驗證 Y 軸字段
      if (
        this.chartData.chartType !== 'multi_line' &&
        this.chartData.chartType !== 'combo' &&
        !this.chartData.yAxisField
      ) {
        alert('Y 軸欄位是必填的。');
        return;
      }

      if (
        (this.chartData.chartType === 'multi_line' || this.chartData.chartType === 'combo') &&
        (!this.chartData.yAxisFields || this.chartData.yAxisFields.length < 2)
      ) {
        alert('請選擇至少兩個 Y 軸欄位。');
        return;
      }

      // 組裝圖表配置數據
      let chartConfig = {
        chart_type: this.chartData.chartType,
        name: this.chartData.name || '未命名圖表',
        data_source: this.chartData.dataSource,
        x_axis_field: this.chartData.xAxisField,
        y_axis_field: this.chartData.yAxisField,
        y_axis_fields:
          (this.chartData.chartType === 'multi_line' ||
          this.chartData.chartType === 'combo' ||
          this.chartData.chartType === 'stacked_bar' ||
          this.chartData.chartType === 'grouped_bar')
          ? this.chartData.yAxisFields.map(field => field.name)
          : [],
        filter_conditions: this.chartData.filterConditions,
        ordering: this.chartData.ordering,
        limit: this.chartData.limit,
        color: this.chartData.color,
      };

      if (this.isEditing) {
        // 如果是編輯模式，發送更新請求
        axios
          .post(`/api/backend/update-chart/${this.chartId}/`, chartConfig)
          .then(async () => {
            alert('圖表已成功更新！');
            await this.$store.dispatch('fetchPermissions'); // 刷新權限
            await this.$emit('reload-charts');
            this.closeModal();
          })
          .catch(error => {
            const errorMsg = error.response?.data?.error || '發生未知錯誤';
            alert(`更新圖表失敗: ${errorMsg}`);
          });
      } else {
        // 如果是新增模式，發送創建請求
        axios
          .post('/api/backend/create-chart/', chartConfig)
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
    },
  },
};
</script>

<style scoped>
.chart-modal-container {
  display: flex;
  flex-direction: row-reverse; /* 讓設定視窗在左邊，預覽視窗在右邊 */
  justify-content: center;
  align-items: stretch;
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  backdrop-filter: blur(5px);
  background: rgba(0, 0, 0, 0.4);
  z-index: 1000;
  /* overflow-y: auto; */
  gap: 20px; /* 調整間距，讓兩個視窗之間有適當的空間 */
  padding: 20px;
  /* padding-left: 200px; 確保左邊的設定窗口有空間 */
  /* margin-left: 50px; 將整個容器右移 */
}

.chart-modal {
  background: #ffffff;
  padding: 10px;
  border-radius: 8px;
  width: 30%;
  height: calc(100vh - 40px); /* 設定固定高度 */
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  /* max-width: 450px;
  max-height: 80vh;
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.2);
  overflow-y: auto;
  animation: fadeIn 0.3s ease-in-out; */
}

.chart-preview-container {
  background: #ffffff;
  padding: 20px;
  border-radius: 8px;
  width: 60%;
  height: calc(100vh - 40px); /* 設定固定高度 */
  /* max-width: 600px;
  max-height: 80vh; */
  box-shadow: 0 10px 15px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  /* overflow-y: auto;
  animation: fadeIn 0.3s ease-in-out; */
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

.chart-modal-footer {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #eee;
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
  /* display: flex;
  flex-direction: column;
  gap: 10px; */
  flex: 1;
  overflow-y: auto; /* 設定區可以滾動 */
  padding-right: 10px; /* 為滾動條預留空間 */
}

.chart-content-settings {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}

.setting {
  margin-bottom: 20px;
  width: 100%;
}

.btn-save,
.btn-cancel {
  background-color: #007bff; /* 保存按鈕背景色 */
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

.chart-summary {
  margin-top: 10px;
  border: 1px solid #eee;
  padding: 8px;
  border-radius: 6px;
  background: #f9f9f9;
}

.chart-preview {
  /* border: 1px solid #ccc;
  padding: 10px;
  border-radius: 6px;
  height: 100%;
  background: #fafafa; */
  flex: 1;
  padding: 15px;
  border-radius: 6px;
  background: #fafafa;
  overflow: hidden; /* 防止圖表溢出 */
}

.chart-modal-body::-webkit-scrollbar {
  width: 6px;
}

.chart-modal-body::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chart-modal-body::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.chart-modal-body::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.chart-modal-header {
  margin-bottom: 20px;
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
