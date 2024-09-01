<template>
    <div>
      <h3>庫存圖表</h3>
      <div id="inventory-chart"></div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import Plotly from 'plotly.js-dist';
  
  export default {
    name: 'TESTInventoryChart',
    data() {
      return {
        inventoryData: [],
      };
    },
    async mounted() {
      await this.fetchInventoryData();
      this.renderChart();
    },
    methods: {
      async fetchInventoryData() {
        try {
          const response = await axios.get('/api/inventory/');
          this.inventoryData = response.data;
        } catch (error) {
          console.error('Error fetching inventory data:', error);
        }
      },
      renderChart() {
        const data = this.inventoryData.map(item => ({
          x: item.product_name,
          y: item.stock_level,
          type: 'bar',
          name: '庫存量',
        }));
  
        const layout = {
          title: '庫存圖表',
          xaxis: { title: '產品' },
          yaxis: { title: '庫存量' },
        };
  
        Plotly.newPlot('inventory-chart', data, layout);
      },
    },
  };
  </script>
  
  <style scoped>
  #inventory-chart {
    width: 100%;
    height: 400px;
  }
  </style>
  