<template>
  <vue-resizable @resize="onResize">
    <div ref="chart" class="plotly-chart"></div>
    <div class="last-updated">最後更新時間:{{ lastUpdated }}</div>
  </vue-resizable>
</template>

<script>
import axios from 'axios';
import Plotly from 'plotly.js-dist';

export default {
  props: ['chartConfig'],
  data() {
    return{
      lastUpdated: ''
    };
  },
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
      } else if (this.chartConfig.name === 'ProductSalesPieChart') {
        apiUrl = '/api/backend/product-sales-pie-chart-data/';
      }

      console.log('Fetching data from:', apiUrl); // 新增這行，確認 API 是否正確
      axios.get(apiUrl)
        .then(response => {
          const data = response.data;
          console.log('Data received:', data); // 新增這行，查看數據是否返回

          let xData, yData;

          if (this.chartConfig.name === 'ProductSalesPieChart') {
            xData = data.categories;
            yData = data.sales;
          } else {
            xData = data.map(item => item.product_name || item.store_name || item.sale_date);
            yData = data.map(item => item.total_amount || item.total_revenue || item.stock_quantity || item.total_sales);
          }

          this.renderChart(xData, yData);
          this.lastUpdated = new Date().toLocaleString();  // 更新最後的更新時間
        })
        .catch(error => {
          console.error('Error fetching chart data:', error);
          alert('無法獲取圖表數據，請稍後再試。');
        });
    },
    renderChart(xData, yData) {
      const chartEl = this.$refs.chart;
      console.log('Rendering chart with data:', xData, yData); // 新增這行

      let trace;

      if (this.chartConfig.name === 'ProductSalesPieChart') {
        trace = {
          labels: xData,
          values: yData,
          type: 'pie'
        };
      } else {
        trace = {
          x: xData,
          y: yData,
          type: this.chartConfig.chartType || 'bar'
        };
      }

      const layout = {
        title: this.chartConfig.label || '圖表',
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

      Plotly.newPlot(chartEl, [trace], layout);
    },
    onResize() {
      if (this.$refs.chart) {
        Plotly.Plots.resize(this.$refs.chart);
      }
    },
    exportData(format) {
      let apiUrl = '';
      if (format === 'csv') {
        apiUrl = '/api/backend/export-data-csv/';
      } else if (format === 'excel') {
        apiUrl = '/api/backend/export-data-excel/';
      } else if (format === 'pdf') {
        apiUrl = '/api/backend/export-data-pdf/';
      }

      axios.post(apiUrl, this.chartConfig)
        .then(response => {
          const url = window.URL.createObjectURL(new Blob([response.data]));
          const link = document.createElement('a');
          link.href = url;
          link.setAttribute('download', format === 'csv' ? 'data.csv' : format === 'excel' ? 'data.xlsx' : 'data.pdf');
          document.body.appendChild(link);
          link.click();
        })
        .catch(error => {
          console.error('Error exporting data:', error);
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

