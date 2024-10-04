<template>
    <div ref="chart" style="width: 100%; height: 100%;"></div>
  </template>
  
  <script>
  import Plotly from 'plotly.js-dist-min';
  
  export default {
    props: ['chartConfig'],
    mounted() {
      this.drawChart();
    },
    methods: {
      drawChart() {
        const chartElement = this.$refs.chart;
        const layout = {
          title: this.chartConfig.label,
          xaxis: {
            title: this.chartConfig.xAxisLabel,
          },
          yaxis: {
            title: this.chartConfig.yAxisLabel,
          },
        };
  
        // 如果是營業額圖表，使用分店名稱 branch_name 作為 x 軸數據
        let xData;
        if (this.chartConfig.name === 'RevenueChart') {
          xData = this.chartConfig.data.map(item => item.branch_name);
        } else {
          xData = this.chartConfig.data.map(item => item.sale_date || item.product_name);
        }
  
        const data = [
          {
            x: xData,
            y: this.chartConfig.data.map(item => item.total_sales || item.stock_quantity),
            type: this.chartConfig.chartType,
          },
        ];
  
        Plotly.newPlot(chartElement, data, layout);
      },
    },
  };
  </script>
  
  <style scoped>
  .chart-wrapper {
    width: 100%;
    height: 100%;
  }
  </style>
  