<template>
  <div ref="chart" class="plotly-chart" @click.stop></div>
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
        dataSource: this.chartConfig.dataSource || '',
        xAxisField: this.chartConfig.xAxisField || '',
        yAxisField: this.chartConfig.yAxisField || '',
        chartType: this.chartConfig.chartType || '', // 使用 chartType
        name: this.chartConfig.name || '',
        id: this.chartConfig.id || null,
        filterConditions: this.chartConfig.filterConditions || '{}',
      },
      chartData: {
        x_data: [],
        y_data: [],
        joinFields: []
      }
    };
  },
  mounted() {
    if (this.localChartConfig.id) {
      this.fetchChartData(this.localChartConfig.id);
    }
    window.addEventListener('resize', this.renderChart);
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
          filter_conditions: JSON.parse(this.localChartConfig.filterConditions || '{}'),
          join_fields: this.chartData.joinFields
        });
        console.log('Chart data response:', response.data);
        
        if (!response.data.x_data || !response.data.y_data) {
          console.error('x_data 或 y_data 缺失:', response.data);
          alert('後端返回的數據格式錯誤，請檢查後端日誌以獲取更多信息。');
          return;
        }

        this.chartData.x_data = response.data.x_data;
        this.chartData.y_data = response.data.y_data;
        this.lastUpdated = response.data.last_updated || new Date().toLocaleString();

        console.log('xData:', this.chartData.x_data);
        console.log('yData:', this.chartData.y_data);

        this.renderChart();
      } catch (error) {
        console.error('獲取圖表數據時出錯:', error);
        alert('獲取圖表數據時出錯，請檢查後端日誌以獲取更多信息。');
      }
    },
    renderChart() {
      const chartEl = this.$refs.chart;
      if (!chartEl) {
        console.error('無法取得圖表的引用（chartEl），請檢查範本中的 ref 是否正確。');
        return;
      }

      console.log('Rendering chart with type:', this.localChartConfig.chartType);
      console.log('x_data:', this.chartData.x_data);
      console.log('y_data:', this.chartData.y_data);

      let trace;
      if (this.localChartConfig.chartType === 'pie') {
        trace = {
          labels: this.chartData.x_data,
          values: this.chartData.y_data,
          type: 'pie',
        };
      } else {
        trace = {
          x: this.chartData.x_data,
          y: this.chartData.y_data,
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
          yAxisField: newConfig.yAxisField || '',
          chartType: newConfig.chartType || '', // 使用 chartType
          name: newConfig.name || '',
          id: newConfig.id || null,
          filterConditions: newConfig.filterConditions || '{}',
        };
        if (this.localChartConfig.id) {
          this.fetchChartData(this.localChartConfig.id);
        }
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
