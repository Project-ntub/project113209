<template>
    <div>
      <h3>銷售圖表</h3>
      <div id="sales-chart"></div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import Plotly from 'plotly.js-dist';
  
  export default {
    name: 'TESTSalesChart',
    data() {
      return {
        salesData: [],
      };
    },
    async mounted() {
      await this.fetchSalesData();
      this.renderChart();
    },
    methods: {
      async fetchSalesData() {
        try {
          const response = await axios.get('/api/sales/');
          this.salesData = response.data;
        } catch (error) {
          console.error('Error fetching sales data:', error);
        }
      },
      renderChart() {
        const data = this.salesData.map(item => ({
          x: item.sale_date,
          y: item.total_amount,
          type: 'line',
          name: '銷售額',
        }));
  
        const layout = {
          title: '銷售圖表',
          xaxis: { title: '日期' },
          yaxis: { title: '銷售額' },
        };
  
        Plotly.newPlot('sales-chart', data, layout);
      },
    },
  };
  </script>
  
  <style scoped>
  #sales-chart {
    width: 100%;
    height: 400px;
  }
  </style>
  