<!-- src/components/backend/PlotlyChart.vue -->
<template> 
  <!-- 圖表容器，使用 Plotly 進行渲染 -->
  <div ref="chart" class="plotly-chart" @click.stop></div>
  <!-- 顯示最後更新時間 -->
  <div class="last-updated">最後更新時間: {{ lastUpdated }}</div>
</template>

<script>
import Plotly from 'plotly.js-dist';

export default {
  // 接收從父組件傳遞過來的圖表配置
  props: ['chartConfig'],
  data() {
    return {
      lastUpdated: '' // 用於顯示圖表的最後更新時間
    };
  },
  mounted() {
    // 組件掛載後渲染圖表，並監聽視窗大小變化以重新渲染圖表
    this.renderChart();
    window.addEventListener('resize', this.renderChart);
  },
  watch: {
    // 監視圖表配置的變化，並在變化時更新最後更新時間及重新渲染圖表
    chartConfig: {
      handler(newConfig) {
        this.lastUpdated = newConfig.last_updated ? new Date(newConfig.last_updated).toLocaleString() : new Date().toLocaleString();
        this.renderChart();
      },
      immediate: true, // 初始時立即執行 handler
      deep: true // 深度監視對象內部變化
    }
  },
  beforeUnmount() {
    // 組件卸載前移除視窗大小變化的事件監聽器
    window.removeEventListener('resize', this.renderChart);
  },
  methods: {
    renderChart() {
      // 獲取圖表的 DOM 元素引用
      const chartEl = this.$refs.chart;
      if (!chartEl) {
        console.error('無法取得圖表的引用（chartEl），請檢查範本中的 ref 是否正確。');
        return;
      }

      console.log('正在渲染圖表，類型:', this.chartConfig.chartType);
      console.log('X 軸資料:', this.chartConfig.x_data);
      console.log('Y 軸資料:', this.chartConfig.y_data);

      // 檢查是否有足夠的資料來渲染圖表
      if (!this.chartConfig.x_data || !this.chartConfig.y_data) {
          console.error('x_data 或 y_data 缺失，無法渲染圖表。');
          return;
      }

      let trace;
      // 根據圖表類型定義 Plotly 的 trace
      if (this.chartConfig.chartType === 'pie') {
          trace = {
              labels: this.chartConfig.x_data,
              values: this.chartConfig.y_data,
              type: 'pie',
          };
      } else {
          trace = {
              x: this.chartConfig.x_data,
              y: this.chartConfig.y_data,
              type: this.chartConfig.chartType || 'bar' // 預設為柱狀圖
          };
      }

      // 定義圖表的佈局
      const layout = {
        title: this.chartConfig.name || '圖表',
        xaxis: { 
          title: this.chartConfig.xAxisField || 'X 軸', // 設定 X 軸標題
          tickangle: -90, // X 軸刻度標籤旋轉角度
          automargin: true // 自動調整邊距
        },
        yaxis: { 
          title: this.chartConfig.yAxisField || 'Y 軸' // 設定 Y 軸標題
        },
        autosize: true, // 自動調整大小
      };

      // 定義 Plotly 的配置選項
      const config = {
        displaylogo: false, // 不顯示 Plotly 標誌
        responsive: true, // 圖表響應式
        modeBarButtonsToRemove: [
          'select2d',     // 移除選擇工具
          'lasso2d',      // 移除套索工具
          'autoScale2d',  // 移除自動縮放工具
        ]
      };

      // 使用 Plotly 渲染圖表
      Plotly.newPlot(chartEl, [trace], layout, config)
        .then(() => {
          console.log('Plotly 圖表成功渲染。');
        })
        .catch(error => {
          console.error('渲染 Plotly 圖表時發生錯誤:', error);
        });
    }
  }
};
</script>

<style scoped>
.plotly-chart {
  width: 100%; /* 圖表寬度佔滿容器 */
  height: 100%; /* 圖表高度佔滿容器 */
}
.last-updated {
  margin-top: 10px;
  font-size: 12px;
  color: #555; /* 顯示最後更新時間的樣式 */
}
</style>
