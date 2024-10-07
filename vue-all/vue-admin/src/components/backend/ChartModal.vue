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
            <label for="chart-style">圖表類型</label>
            <select id="chart-style" v-model="chartData.style">
              <option value="bar">柱狀圖</option>
              <option value="line">折線圖</option>
              <option value="pie">餅圖</option>
              <!-- 更多圖表類型 -->
            </select>
          </div>
          <!-- 資料來源 -->
          <div class="setting">
            <label for="data-source">資料來源</label>
            <select id="data-source" v-model="chartData.dataSource">
              <option v-for="source in dataSource" :key="source.value" :value="source.value">
                {{ source.label }}
              </option>
            </select>
          </div>
          <!-- X 軸和 Y 軸欄位 -->
          <!-- X 軸欄位選擇 -->
          <div class="setting">
            <label for="x-axis-field">X 軸欄位</label>
            <select id="x-axis-field" v-model="chartData.xAxisField">
              <!-- 當前模型的欄位 -->
              <option v-for="field in tableFields" :key="field" :value="field">
                {{ field }}
              </option>
              <!-- 關聯模型的欄位 -->
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
          <div id="chart-container"></div>
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
import Plotly from 'plotly.js-dist';

export default {
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
        style: 'bar',
        name: '',
        dataSource: '',
        xAxisField: '',
        yAxisField: '',
        filterConditions: '{}',
        x_data: [],
        y_data: [], 
        joinFields: []
      },
      joinableFields: [], //可用關聯欄位
      dataSource: [],
      tableFields: []
    };
  },
  mounted() {
    this.fetchDataSources();
    if (this.isEditing && this.chartId) {
      this.fetchChartConfig(this.chartId)
        .then(config => {
          if (config) {
            this.chartData = {
              ...this.chartData,
              ...config
            };
            this.fetchTableFields();
          }
        });
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
    fetchChartData() {
      let filterConditions = {};
      try {
        filterConditions = JSON.parse(this.chartData.filterConditions || '{}');
      } catch (error) {
        console.error('過濾條件格式無效，使用預設值 {}');
      }

      axios.get(`/api/backend/chart-data/${this.chartData.dataSource}/`, {
        params: {
          x_field: this.chartData.xAxisField,
          y_field: this.chartData.yAxisField,
          filter_conditions: JSON.stringify(filterConditions)
        }
      }).then(response => {
        const { x_data, y_data } = response.data;

        if (x_data && y_data) {
          this.chartData.x_data = x_data;
          this.chartData.y_data = y_data;
          this.renderChart();
        } else {
          console.error('x_data 和 y_data 不能為空');
        }
      }).catch(error => {
        console.error('獲取圖表數據時出錯:', error);
      });
    },
    renderChart() {
      const trace = {
        x: this.chartData.x_data,
        y: this.chartData.y_data,
        type: this.chartData.style || 'bar'
      };

      const layout = {
        title: this.chartData.name || '圖表預覽',
        xaxis: { title: this.chartData.xAxisField || 'X 軸' },
        yaxis: { title: this.chartData.yAxisField || 'Y 軸' }
      };

      const config = {
        displaylogo: false, 
        modeBarButtonsToRemove: [
          'select2d',     
          'lasso2d',      
          'autoScale2d'
        ]
      };

      Plotly.newPlot('chart-container', [trace], layout, config);
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
        chart_type: this.chartData.style,
        name: this.chartData.name || '未命名圖表',
        data_source: this.chartData.dataSource,
        x_axis_field: this.chartData.xAxisField,
        y_axis_field: this.chartData.yAxisField,
        filter_conditions: filterConditions,
        x_data: this.chartData.x_data,
        y_data: this.chartData.y_data
      };

      axios.post('/api/backend/create-chart/', chartConfig)
        .then(response => {
          alert('圖表已成功創建！');
          this.$emit('chart-saved', response.data);
          this.closeModal();
        })
        .catch(error => {
          const errorMsg = error.response?.data?.error || '發生未知錯誤';
          alert(`創建圖表失敗: ${errorMsg}`);
        });
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
}
.chart-modal {
  background: #fff;
  padding: 20px;
  border-radius: 10px;
  width: 80%;
  max-width: 600px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
.chart-modal-header,
.chart-modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.chart-modal-body {
  display: flex;
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
  width: 100%
}

#chart-container {
  width: 100%;
  height: 100%;
}

.setting {
  margin-bottom: 15px;
}
.btn-preview,
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