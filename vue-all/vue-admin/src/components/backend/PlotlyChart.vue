<template>
  <div ref="chart" class="plotly-chart"></div>
  <div class="last-updated">最後更新時間:{{ lastUpdated }}</div>
</template>

<script>
import axios from 'axios';
import Plotly from 'plotly.js-dist';

export default {
  props: ['chartConfig'],
  data() {
    return {
      lastUpdated: '',
      localChartConfig: { ...this.chartConfig }  // 複製 chartConfig 到本地數據
    };
  },
  mounted() {
    this.fetchChartData();
  },
  methods: {
    fetchChartData() {
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
      }

      axios.get(apiUrl)
        .then(response => {
          const data = response.data;
          console.log("Fetched data from API: ", data);  // 打印從 API 獲取的數據

          let xData, yData;
          if (this.localChartConfig.name === 'ProductSalesPieChart') {
            xData = data.categories;
            yData = data.sales;
          } else {
            xData = data.map(item => item.product_name || item.store_name || item.sale_date);
            yData = data.map(item => item.total_amount || item.total_revenue || item.stock_quantity || item.total_sales);
          }

          this.renderChart(xData, yData);

          // 將加載的數據保存到 localChartConfig.data 中
          this.localChartConfig.data = xData.map((x, i) => ({
            x,
            y: yData[i]
          }));

          console.log("localChartConfig after data load: ", this.localChartConfig);  // 打印 localChartConfig 看它是否包含數據

          this.lastUpdated = new Date().toLocaleString();
        })
        .catch(error => {
          console.error('Error fetching chart data:', error);
          alert('無法獲取圖表數據，請稍後再試。');
        });
    },
    renderChart(xData, yData) {
      const chartEl = this.$refs.chart;

      let trace;
      if (this.localChartConfig.name === 'ProductSalesPieChart') {
        trace = {
          labels: xData,
          values: yData,
          type: 'pie'
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
          title: this.localChartConfig.xAxisLabel || 'X 轴',
          tickangle: -90,
          automargin: true
        },
        yaxis: { 
          title: this.localChartConfig.yAxisLabel || 'Y 轴'
        },
        width: this.localChartConfig.width || 600,
        height: this.localChartConfig.height || 400
      };

      const config = {
        displaylogo: false, // 隱藏Plotly的logo
        modeBarButtonsToRemove: [
          'select2d',     // 隱藏 box select
          'lasso2d',      // 隱藏 lasso select
          'autoScale2d',  // 隱藏 autoscale
        ]
      }

      Plotly.newPlot(chartEl, [trace], layout, config);
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
.last-updated {
  margin-top: 10px;
  font-size: 12px;
  color: #555;
}
</style>
