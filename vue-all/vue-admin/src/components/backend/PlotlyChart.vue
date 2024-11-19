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
        this.lastUpdated = newConfig.last_updated
          ? new Date(newConfig.last_updated).toLocaleString()
          : new Date().toLocaleString();
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

      const color = (this.chartConfig.color && this.chartConfig.color.hex) || '#000000'; // 提取颜色值
      const threshold = this.chartConfig.threshold;

      let data = [];
      const layout = {
        title: this.chartConfig.name || '圖表',
        xaxis: {
          title: this.chartConfig.xAxisField || 'X 軸',
          tickangle: -90,
          automargin: true
        },
        yaxis: {
          title: this.chartConfig.yAxisField || 'Y 軸'
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

      if (this.chartConfig.chartType === 'multi_line') {
        let traces = [];
        const x_data = this.chartConfig.x_data;
        const y_data = this.chartConfig.y_data;
        for (const [y_field, y_values] of Object.entries(y_data)) {
          traces.push({
            x: x_data,
            y: y_values,
            type: 'scatter',
            mode: 'lines',
            name: y_field,
            line: { color: color },
          });
        }
        data = traces;
      } else if (this.chartConfig.chartType === 'heatmap') {
        data = [{
          z: this.chartConfig.z_data,
          x: this.chartConfig.x_data,
          y: this.chartConfig.y_data,
          type: 'heatmap',
        }];
      } else if (this.chartConfig.chartType === 'combo') {
        const trace1 = {
          x: this.chartConfig.x_data,
          y: this.chartConfig.y_data_bar,
          type: 'bar',
          name: '柱狀圖數據',
          marker: { color: color },
          yaxis: 'y1',
        };
        const trace2 = {
          x: this.chartConfig.x_data,
          y: this.chartConfig.y_data_line,
          type: 'scatter',
          mode: 'lines+markers',
          name: '折線圖數據',
          line: { color: color },
          yaxis: 'y2',
        };
        data = [trace1, trace2];
        layout.yaxis2 = {
          title: this.chartConfig.yAxisFieldLine,
          overlaying: 'y',
          side: 'right',
        };
      } else if (this.chartConfig.chartType === 'horizontal_bar') {
        let marker = { color: color };
        if (threshold !== null && threshold !== undefined) {
          const colors = this.chartConfig.x_data.map(value => value >= threshold ? 'red' : 'blue');
          marker = { color: colors };
        }
        data = [{
          x: this.chartConfig.x_data,
          y: this.chartConfig.y_data,
          type: 'bar',
          orientation: 'h',
          marker: marker,
        }];
      } else {
        // 默認處理
        if (this.chartConfig.chartType === 'pie') {
          data = [{
            labels: this.chartConfig.x_data,
            values: this.chartConfig.y_data,
            type: 'pie',
          }];
        } else {
          let marker = { color: color };
          if (threshold !== null && threshold !== undefined) {
            const colors = this.chartConfig.y_data.map(value => value >= threshold ? 'red' : 'blue');
            marker = { color: colors };
          }

          data = [{
            x: this.chartConfig.x_data,
            y: this.chartConfig.y_data,
            type: this.chartConfig.chartType || 'bar',
            marker: marker,
            line: { color: color },
          }];
        }
      }

      Plotly.newPlot(chartEl, data, layout, config);
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
