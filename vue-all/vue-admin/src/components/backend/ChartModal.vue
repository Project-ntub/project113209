<template>
  <div class="chart-modal-container">
    <div class="chart-modal">
      <div class="chart-modal-header">
        <h2>{{ isEditing ? '編輯圖表' : '新增圖表' }}</h2>
        <button @click="closeModal" class="close-btn">×</button>
      </div>
      <div class="chart-modal-body">
        <div class="chart-settings">
          <!-- 圖表類型 -->
          <div class="setting">
            <label for="chart-style">圖表類型</label>
            <select id="chart-style" v-model="chartData.style">
              <option value="bar">柱狀圖</option>
              <option value="line">折線圖</option>
              <option value="pie">圓餅圖</option>
              <option value="radar">雷達圖</option>
              <option value="scatter">散點圖</option>
              <!-- 更多圖表類型 -->
            </select>
          </div>
          <!-- 數據來源 -->
          <div class="setting">
            <label for="data-source">數據來源</label>
            <select id="data-source" v-model="chartData.dataSource">
              <option v-for="source in dataSource" :key="source.value" :value="source.value">
                {{ source.label }}
              </option>
            </select>
          </div>
          <!-- X軸和Y軸字段 -->
          <div class="setting">
            <label for="x-axis-field">X軸欄位</label>
            <select id="x-axis-field" v-model="chartData.xAxisField">
              <option v-for="field in tableFields" :key="field" :value="field">
                {{ field }}
              </option>
            </select>
          </div>
          <div class="setting">
            <label for="y-axis-field">Y軸欄位</label>
            <select id="y-axis-field" v-model="chartData.yAxisField">
              <option v-for="field in tableFields" :key="field" :value="field">
                {{ field }}
              </option>
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
        <button class="btn-preview" @click="previewChart">預覽圖表</button>
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
    chartId: { // 新增 chartId 用來識別是否為編輯模式
      type: Number,
      default: null
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
        y_data: []
      },
      dataSource: [],  // 用於存儲從後端獲取的資料來源選項
      tableFields: [] // 確保初始化tableFields為空數組
    };
  },
  methods: {
    fetchDataSources() {
      axios.get('/api/backend/data-sources/')
        .then(response => {
          this.dataSource = response.data;  // 將選項存儲在 dataSources 中
        })
        .catch(error => {
          console.error('獲取資料來源出錯:', error);
        });
    },
    fetchTableFields() {
      if (this.chartData.dataSource) {
        axios.get(`/api/backend/table-fields/${this.chartData.dataSource}/`)
          .then(response => {
            this.tableFields = response.data;  // 確認這裡的賦值是正確的
          })
          .catch(error => {
            console.error('獲取欄位名稱出錯:', error);
          });
      }
    },
    fetchData() {
      if (this.isEditing && this.chartId) {
        // 修正 API 路徑
        axios.get(`/api/backend/charts/${this.chartId}/`)
          .then(response => {
            const data = response.data;
            this.chartData.style = data.chart_type;
            this.chartData.name = data.name;
            this.chartData.dataSource = data.dataSource;
            this.chartData.xAxisField = data.xAxisField;
            this.chartData.yAxisField = data.yAxisField;
            this.chartData.filterConditions = JSON.stringify(data.filterConditions);
            this.chartData.x_data = data.x_data;
            this.chartData.y_data = data.y_data;
          })
          .catch(error => {
            console.error('加載圖表數據時出錯', error);
          });
      }
    },
    saveChart() {
      // 確保 filterConditions 是 JSON 格式的字典
      let filterConditions = {};
      try {
        filterConditions = JSON.parse(this.chartData.filterConditions);
      } catch (error) {
        alert("過濾條件格式無效，請輸入正確的 JSON 格式。");
        return;
      }

      // 根據用戶選擇的資料來源和欄位來生成 x_data 和 y_data
      axios.get(`/api/backend/chart-data/${this.chartData.dataSource}/`, {
        params: {
          x_field: this.chartData.xAxisField,
          y_field: this.chartData.yAxisField,
          filter_conditions: JSON.stringify(filterConditions)
        }
      }).then(response => {
        const { x_data, y_data } = response.data;

        if (x_data && y_data) {
          let chartConfig = {
            chart_type: this.chartData.style,
            name: this.chartData.name || 'Unnamed Chart',
            data_source: this.chartData.dataSource,
            x_axis_field: this.chartData.xAxisField,
            y_axis_field: this.chartData.yAxisField,
            x_data: x_data,
            y_data: y_data
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
        } else {
          alert('x_data 和 y_data 不能為空，請輸入有效數據');
        }
      }).catch(error => {
        console.error('獲取圖表數據時出錯:', error);
        alert('無法獲取圖表數據，請稍後再試。');
      });
    },
    previewChart() {
      // 檢查 x_data 和 y_data 是否為空
      if (!this.chartData.x_data.length || !this.chartData.y_data.length) {
        alert('x_data 和 y_data 不能為空，請輸入有效數據');
        return;
      }

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

      Plotly.newPlot('chart-container', [trace], layout);
    },
    closeModal() {
      this.$emit('close');
    }
  },
  watch: {
    'chartData.dataSource': function(newDataSource) {
      if (newDataSource) {
        this.fetchTableFields();  // 動態加載欄位
      }
    }
  },
  mounted() {
    this.fetchData(); // 在組件加載時調用此方法
    this.fetchDataSources(); // 加載組件時獲取資料來源選項
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
  height: 400px;
}

#chart-container {
  width: 100%;
  height: 100%; /* 確保圖表填滿容器 */
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
