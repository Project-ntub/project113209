<!-- src/components/backend/PlotlyChart.vue -->
<template> 
  <div ref="chart" class="plotly-chart" @click.stop></div>
  <div class="last-updated">最後更新時間: {{ lastUpdated }}</div>
</template>

<script>
import Plotly from 'plotly.js-dist';

export default {
  props: ['chartConfig'],
  data() {
    return {
      lastUpdated: ''
    };
  },
  mounted() {
    this.renderChart();
    window.addEventListener('resize', this.renderChart);
  },
  watch: {
    chartConfig: {
      handler(newConfig) {
        this.lastUpdated = newConfig.last_updated ? new Date(newConfig.last_updated).toLocaleString() : new Date().toLocaleString();
        this.renderChart();
      },
      immediate: true,
      deep: true
    }
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.renderChart);
  },
  methods: {
    renderChart() {
      const chartEl = this.$refs.chart;
      if (!chartEl) {
        console.error('無法取得圖表的引用（chartEl），請檢查範本中的 ref 是否正確。');
        return;
      }

      console.log('Rendering chart with type:', this.chartConfig.chartType);
      console.log('x_data:', this.chartConfig.x_data);
      console.log('y_data:', this.chartConfig.y_data);

      if (!this.chartConfig.x_data || !this.chartConfig.y_data) {
          console.error('x_data 或 y_data 缺失，無法渲染圖表。');
          return;
      }

      let trace;
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
              type: this.chartConfig.chartType || 'bar'
          };
      }

      const layout = {
        title: this.chartConfig.name || '圖表',
        xaxis: { 
          title: this.chartConfig.xAxisField || 'X 軸', // 使用駝峰命名
          tickangle: -90,
          automargin: true
        },
        yaxis: { 
          title: this.chartConfig.yAxisField || 'Y 軸' // 使用駝峰命名
        },
        autosize: true,
      };

      const config = {
        displaylogo: false, 
        responsive: true,
        modeBarButtonsToRemove: [
          'select2d',     
          'lasso2d',      
          'autoScale2d',  
        ]
      };

      Plotly.newPlot(chartEl, [trace], layout, config)
        .then(() => {
          console.log('Plotly chart rendered successfully.');
        })
        .catch(error => {
          console.error('Error rendering Plotly chart:', error);
        });
    }
  }
};
</script>

<style scoped>
.plotly-chart {
  width: 100%;
  height: 100%;
}
.last-updated {
  margin-top: 10px;
  font-size: 12px;
  color: #555;
}
</style>
