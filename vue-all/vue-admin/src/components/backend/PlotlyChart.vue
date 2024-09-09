<template>
  <div ref="chart" class="plotly-chart"></div>
</template>

<script>
import Plotly from 'plotly.js-dist';
import axios from 'axios';

export default {
  props: ['chartConfig'],
  mounted() {
    this.fetchChartData(); // 在组件挂载时调用获取数据的方法
    this.renderChart();
  },
  methods: {
    fetchChartData() {
      axios.get('/api/backend/sales-chart-data/') // 替换为您的实际 API 路径
        .then(response => {
          const { data, layout } = response.data;  // 从后端响应获取数据
          this.renderChart(data, layout);
        })
        .catch(error => {
          console.error('Error fetching chart data:', error);
        });
    },
    renderChart() {
      const chartEl = this.$refs.chart; // 假设你有一个 ref 名为 chart 的元素
      if (!chartEl) {
        console.error('Chart element is not available.');
        return;
      }

      const data = [{ x: [1, 2, 3], y: [2, 6, 3], type: 'scatter' }];
      const layout = { title: 'A Simple Plot' };

      Plotly.newPlot(chartEl, data, layout);
    }
  },
  watch: {
    chartConfig: {
      deep: true,
      handler() {
        this.fetchChartData(); // 当 chartConfig 改变时，重新获取数据
      }
    }
  }
};
</script>

<style scoped>
.plotly-chart {
  width: 100%;
  height: 100%;
}
</style>
