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
      localChartConfig: {
        ...this.chartConfig,
        dataSource: this.chartConfig.data_source || '',
        xAxisField: this.chartConfig.x_axis_field || '',
        yAxisField: this.chartConfig.y_axis_field || '',
        chartType: this.chartConfig.chart_type || '',
        name: this.chartConfig.name || '',
        label: this.chartConfig.label || '',
      },
      chartData: {
        xAxisField: [],
        yAxisField: []
      }
    };
  },
  mounted() {
    if (!this.$refs.chart) {
      console.error('无法获取图表的引用（this.$refs.chart），请检查模板中的 ref 是否正确。');
      return;
    }
    this.fetchChartData(this.localChartConfig.id);
  },
  methods: {
    async fetchChartData(chartId) {
      if (!this.localChartConfig.dataSource || !this.localChartConfig.xAxisField || !this.localChartConfig.yAxisField) {
        console.error('資料來源、X軸或Y軸字段未提供');
        alert('資料來源、X軸或Y軸字段未提供');
        return; 
      }

      try {
        console.log('Fetching chart data with:', {
          table_name: this.localChartConfig.dataSource,
          x_field: this.localChartConfig.xAxisField,
          y_field: this.localChartConfig.yAxisField,
          chart_id: chartId
        });
        const response = await axios.post('/api/backend/dynamic-chart-data/', {
          table_name: this.localChartConfig.dataSource,
          x_field: this.localChartConfig.xAxisField,
          y_field: this.localChartConfig.yAxisField,
          chart_id: chartId
        });
        console.log('Chart data response:', response.data);
        const data = response.data;
        // 檢查是否有錯誤
        if (data.error) {
          console.error('後端返回錯誤:', data.error);
          alert('後端返回錯誤: ' + data.error);
          return;
        }

        // 檢查 x_data 和 y_data 是否存在
        if (!data.x_data || !data.y_data) {
          console.error('x_data 或 y_data 缺失:', data);
          alert('後端返回的數據格式錯誤，請檢查後端日誌以獲取更多信息。');
          return;
        }
        this.chartData.xAxisField = data.x_data;
        this.chartData.yAxisField = data.y_data;

        // 在调用 renderChart 之前，添加调试信息
        console.log('xData:', this.chartData.xAxisField);
        console.log('yData:', this.chartData.yAxisField);

        this.renderChart(this.chartData.xAxisField, this.chartData.yAxisField);
      } catch (error) {
        console.error('獲取圖表數據時出錯:', error);
        alert('獲取圖表數據時出錯，請檢查後端日誌以獲取更多信息。');
      }
    },
    renderChart(xData, yData) {
      const chartEl = this.$refs.chart;
      if (!chartEl) {
        console.error('无法获取图表的引用（chartEl），请检查模板中的 ref 是否正确。');
        return;
      }

      let trace;
      if (this.localChartConfig.chartType === 'pie') {
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
        title: this.localChartConfig.name || '圖表',
        xaxis: { 
          title: this.localChartConfig.xAxisField || 'X 軸',
          tickangle: -90,
          automargin: true
        },
        yaxis: { 
          title: this.localChartConfig.yAxisField || 'Y 軸'
        },
        autosize: true,
      };

      const config = {
        displaylogo: false, 
        responsive: true,
        modeBarButtonsToRemove: [
          'select2d',     
          'lasso2d',      
          'autoScale2d',  
        ]
      };

      Plotly.newPlot(chartEl, [trace], layout, config);
    }
  },
  watch: {
    chartConfig: {
      handler(newConfig) {
        this.localChartConfig = {
          ...newConfig,
          dataSource: newConfig.dataSource || '',
          xAxisField: newConfig.xAxisField || '',
          yAxisField: newConfig.yAxisField || ''
        };
        this.fetchChartData(newConfig.id);  // 根據新的配置重新加載圖表數據
      },
      immediate: true,
      deep: true
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
