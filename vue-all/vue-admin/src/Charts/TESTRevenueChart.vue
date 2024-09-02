<template>
    <div>
      <h3>營業額圖表</h3>
      <div id="revenue-chart"></div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import Plotly from 'plotly.js-dist';
  
  export default {
    name: 'TESTRevenueChart',
    data() {
      return {
        revenueData: [],
      };
    },
    async mounted() {
      await this.fetchRevenueData();
      this.renderChart();
    },
    methods: {
      async fetchRevenueData() {
        try {
          const response = await axios.get('/api/revenue/');
          this.revenueData = response.data;
        } catch (error) {
          console.error('Error fetching revenue data:', error);
        }
      },
      renderChart() {
        const data = this.revenueData.map(item => ({
          x: item.revenue_date,
          y: item.total_revenue,
          type: 'bar',
          name: '營業額',
        }));
  
        const layout = {
          title: '營業額圖表',
          xaxis: { title: '日期' },
          yaxis: { title: '營業額' },
        };
  
        Plotly.newPlot('revenue-chart', data, layout);
      },
    },
  };
  </script>
  
  <style scoped>
  #revenue-chart {
    width: 100%;
    height: 400px;
  }
  </style>
  