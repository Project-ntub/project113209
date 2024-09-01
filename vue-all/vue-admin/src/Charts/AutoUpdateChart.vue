<template>
    <div id="chart-div"></div>
  </template>
  
  <script>
  import axios from 'axios';
  import Plotly from 'plotly.js-dist';
  
  export default {
    data() {
      return {
        chartData: null,
        updateInterval: 60000 // 更新間隔時間，例如每60秒更新一次
      };
    },
    mounted() {
      this.fetchChartData();
      this.startAutoUpdate();
    },
    methods: {
      fetchChartData() {
        axios.get('/api/update-chart-data/')
          .then(response => {
            this.chartData = response.data;
            this.renderChart();
          })
          .catch(error => {
            console.error('Error fetching chart data:', error);
          });
      },
      renderChart() {
        Plotly.react('chart-div', this.chartData.data, this.chartData.layout);
      },
      startAutoUpdate() {
        setInterval(this.fetchChartData, this.updateInterval);
      }
    }
  };
  </script>
  