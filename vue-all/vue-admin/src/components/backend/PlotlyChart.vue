<template>
  <div ref="chart" class="plotly-chart"></div>
  <div class="last-updated">最後更新時間: {{ lastUpdated }}</div>
</template>

<script>
import axios from 'axios';
import Plotly from 'plotly.js-dist';

export default {
  props: ['chartConfig'],
  data() {
    return {
      lastUpdated: '',
      localChartConfig: { ...this.chartConfig } // 複製 chartConfig 到本地數據
    };
  },
  mounted() {
    this.fetchChartData();
  },
  methods: {
    async fetchChartData() {
      let apiUrl = '';
      switch (this.localChartConfig.name) {
        case 'SalesChart':
          apiUrl = '/api/backend/sales-chart-data/';
          break;
        case 'RevenueChart':
          apiUrl = '/api/backend/revenue-chart-data/';
          break;
        case 'InventoryChart':
          apiUrl = '/api/backend/inventory-chart-data/';
          break;
        case 'ProductSalesPieChart':
          apiUrl = '/api/backend/product-sales-pie-chart-data/';
          break;
        default:
          console.error('Unknown chart type');
          return;
      }

      try {
        const response = await axios.get(apiUrl);
        const data = response.data;
        console.log("Fetched data from API: ", data);

        let xData, yData;
        if (this.localChartConfig.name === 'ProductSalesPieChart') {
          xData = data.categories;
          yData = data.sales;
        } else {
          xData = data.map(item => item.product_name || item.store_name || item.sale_date);
          yData = data.map(item => item.total_amount || item.total_revenue || item.stock_quantity || item.total_sales);
        }

        this.renderChart(xData, yData);

        // 將 data 設置到 chartConfig 中
        this.localChartConfig.data = xData.map((x, i) => ({
          x,
          y: yData[i]
        }));

        console.log("localChartConfig after data load: ", this.localChartConfig);

        // 通知父組件 chartConfig 已更新
        this.$emit('update-chart-config', this.localChartConfig);

        this.lastUpdated = new Date().toLocaleString();
      } catch (error) {
        console.error('Error fetching chart data:', error);
        alert('無法獲取圖表數據，請稍後再試。');
      }
    },
    renderChart(xData, yData) {
      const chartEl = this.$refs.chart;

      let trace;
      if (this.localChartConfig.name === 'ProductSalesPieChart') {
        trace = {
          labels: xData,
          values: yData,
          type: 'pie',
        };
      } else {
        trace = {
          x: xData,
          y: yData,
          type: this.localChartConfig.chartType || 'bar'
        };
      }

      const layout = {
        title: this.localChartConfig.label || '圖表',
        xaxis: { 
          title: this.localChartConfig.xAxisLabel || 'X 軸',
          tickangle: -90,
          automargin: true
        },
        yaxis: { 
          title: this.localChartConfig.yAxisLabel || 'Y 軸'
        },
        width: this.localChartConfig.width || 600,
        height: this.localChartConfig.height || 400
      };

      const config = {
        displaylogo: false, 
        modeBarButtonsToRemove: [
          'select2d',     
          'lasso2d',      
          'autoScale2d',  
        ]
      };

      Plotly.newPlot(chartEl, [trace], layout, config);
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
