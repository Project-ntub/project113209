<template>
  <vue-resizable @resize="onResize">
    <div ref="chart" class="plotly-chart"></div>
  </vue-resizable>
</template>

<script>
import axios from 'axios';
import Plotly from 'plotly.js-dist';

export default {
  props: ['chartConfig'],
  mounted() {
    this.fetchChartData();
  },
  methods: {
    fetchChartData() {
      let apiUrl = '';
      if (this.chartConfig.name === 'SalesChart') {
        apiUrl = '/api/backend/sales-chart-data/';
      } else if (this.chartConfig.name === 'RevenueChart') {
        apiUrl = '/api/backend/revenue-chart-data/';
      } else if (this.chartConfig.name === 'InventoryChart') {
        apiUrl = '/api/backend/inventory-chart-data/';
      } else if (this.chartConfig.name === 'SalesVolumeChart') {
        apiUrl = '/api/backend/sales-volume-chart-data/';
      } else if (this.chartConfig.name === 'StoreComparisonChart') {
        apiUrl = '/api/backend/store-comparison-chart-data/';
      }

      axios.get(apiUrl)
        .then(response => {
          const data = response.data;
          const xData = data.map(item => item.product_name || item.store_name || item.sale_date);
          const yData = data.map(item => item.total_amount || item.total_revenue || item.stock_quantity);
          this.renderChart(xData, yData);
        })
        .catch(error => {
          console.error('Error fetching chart data:', error);
        });
    },
    renderChart(xData, yData) {
      const chartEl = this.$refs.chart;
      const layout = {
        title: this.chartConfig.label,
        xaxis: { 
          title: this.chartConfig.xAxisLabel || 'X 轴',
          tickangle: -90,
          automargin: true
        },
        yaxis: { 
          title: this.chartConfig.yAxisLabel || 'Y 轴'
        },
        width: this.chartConfig.width || 600,
        height: this.chartConfig.height || 400
      };

      Plotly.newPlot(chartEl, [{
        x: xData,
        y: yData,
        type: this.chartConfig.chartType || 'bar'
      }], layout);
    },
    onResize() {
      if (this.$refs.chart) {
        Plotly.Plots.resize(this.$refs.chart);
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
