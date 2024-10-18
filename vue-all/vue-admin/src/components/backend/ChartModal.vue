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
            <select id="data-source" v-model="chartData.dataSource" @change="fetchTableFields">
              <option v-for="source in dataSource" :key="source.value" :value="source.value">
                {{ source.label }}
              </option>
            </select>
          </div>
          <!-- X 軸欄位選擇 -->
          <div class="setting">
            <label for="x-axis-field">X 軸欄位</label>
            <select id="x-axis-field" v-model="chartData.xAxisField">
              <option v-for="field in tableFields" :key="field" :value="field">
                {{ field }}
              </option>
              <optgroup v-for="(relatedField, key) in joinableFields" :key="key" :label="`關聯欄位：${key}`">
                <option v-for="field in relatedField.fields" :key="field" :value="`${key}__${field}`">
                  {{ field }}
                </option>
              </optgroup>
            </select>
          </div>

          <!-- Y 軸欄位選擇 -->
          <div class="setting">
            <label for="y-axis-field">Y 軸欄位</label>
            <select id="y-axis-field" v-model="chartData.yAxisField">
              <option v-for="field in tableFields" :key="field" :value="field">
                {{ field }}
              </option>
              <optgroup v-for="(relatedField, key) in joinableFields" :key="key" :label="`關聯欄位：${key}`">
                <option v-for="field in relatedField.fields" :key="field" :value="`${key}__${field}`">
                  {{ field }}
                </option>
              </optgroup>
            </select>
          </div>

          <!-- 過濾條件 -->
          <div class="setting">
            <label for="filter-conditions">過濾條件</label>
            <textarea id="filter-conditions" v-model="chartData.filterConditions" placeholder="輸入過濾條件 (JSON格式)" rows="3"></textarea>
          </div>
        </div>
        <!-- 圖表預覽 -->
        <div class="chart-preview">
          <h3>預覽</h3>
          <PlotlyChart :chartConfig="chartData" /> <!-- 使用 PlotlyChart 組件進行渲染 -->
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

export default {
  components: {
    PlotlyChart
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
        filterConditions: '{}',
        x_data: [],
        y_data: [],
        joinFields: []
      },
      joinableFields: [],
      dataSource: [],
      tableFields: []
    };
  },
  mounted() {
    this.fetchDataSources();
    if (this.isEditing && this.chartId) {
      axios.get(`/api/backend/charts/${this.chartId}/`)
        .then(response => {
          const config = response.data;
          this.chartData = {
            ...this.chartData,
            id: config.id,
            chartType: config.chartType,
            name: config.name,
            dataSource: config.dataSource,
            xAxisField: config.xAxisField,
            yAxisField: config.yAxisField,
            filterConditions: JSON.stringify(config.filter_conditions || '{}'),
          };
          if (this.chartData.dataSource) {
            this.$nextTick(() => {
              this.fetchTableFields();
            });
          }
        })
        .catch(error => {
          console.error('獲取圖表配置出錯:', error);
          alert('獲取圖表配置時出錯，請檢查後端日誌以獲取更多信息。');
        });
    }
  },
  watch: {
    'chartData.dataSource'() {
      this.fetchTableFields();
    },
    'chartData.xAxisField'() {
      if (this.chartData.dataSource && this.chartData.yAxisField) {
        this.fetchChartData();
      }
    },
    'chartData.yAxisField'() {
      if (this.chartData.dataSource && this.chartData.xAxisField) {
        this.fetchChartData();
      }
    }
  },
  methods: {
    fetchDataSources() {
      axios.get('/api/backend/data-sources/')
        .then(response => {
          this.dataSource = response.data;
        })
        .catch(error => {
          console.error('獲取資料來源出錯:', error);
        });
    },
    fetchTableFields() {
      if (this.chartData.dataSource) {
        axios.get(`/api/backend/table-fields/${this.chartData.dataSource}/`)
          .then(response => {
            this.tableFields = response.data.fields;
            this.joinableFields = response.data.related_fields;
            if (this.isEditing && this.chartData.xAxisField && this.chartData.yAxisField) {
              this.$nextTick(() => {
                this.fetchChartData();
              });
            }
          })
          .catch(error => {
            console.error('獲取欄位名稱出錯:', error);
          });
      }
    },
    async fetchChartData() {
      let filterConditions = {};
      try {
        filterConditions = JSON.parse(this.chartData.filterConditions || '{}');
      } catch (error) {
        console.error('過濾條件格式無效，使用預設值 {}');
      }

      try {
        const response = await axios.post('/api/backend/dynamic-chart-data/', {
          table_name: this.chartData.dataSource,
          x_field: this.chartData.xAxisField,
          y_field: this.chartData.yAxisField,
          filter_conditions: filterConditions,
          join_fields: this.chartData.joinFields
        });
        const { x_data, y_data } = response.data;
        if (x_data && y_data) {
          this.chartData.x_data = x_data;
          this.chartData.y_data = y_data;
        } else {
          console.error('x_data 和 y_data 不能為空');
        }
      } catch (error) {
        console.error('獲取圖表數據時出錯:', error);
      }
    },
    saveChart() {
      let filterConditions = {};
      try {
        filterConditions = JSON.parse(this.chartData.filterConditions || '{}');
      } catch (error) {
        alert('過濾條件格式無效，請輸入正確的 JSON 格式。');
        return;
      }

      let chartConfig = {
        chart_type: this.chartData.chartType,
        name: this.chartData.name || '未命名圖表',
        data_source: this.chartData.dataSource,
        x_axis_field: this.chartData.xAxisField,
        y_axis_field: this.chartData.yAxisField,
        filter_conditions: filterConditions,
      };

      if (this.isEditing) {
        axios.post(`/api/backend/update-chart/${this.chartId}/`, chartConfig)
          .then(() => {
            alert('圖表已成功更新！');
            this.$emit('reload-charts');
            this.closeModal();
          })
          .catch(error => {
            const errorMsg = error.response?.data?.error || '發生未知錯誤';
            alert(`更新圖表失敗: ${errorMsg}`);
          });
      } else {
        // 創建模式，調用創建 API
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
  max-width: 600px;
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
</style>
