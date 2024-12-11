<!-- src/components/backend/PlotlyChart.vue -->
<template>
  <!-- 圖表容器，使用 Plotly 進行渲染 -->
  <div ref="chart" class="plotly-chart" @click.stop></div>
  <!-- 顯示最後更新時間 -->
  <div class="last-updated">最後更新時間: {{ lastUpdated }}</div>
</template>

<script>
import Plotly from 'plotly.js-dist';

export default {
  props: ['chartConfig'],
  
  data() {
    return {
      lastUpdated: ''
    };
  },
  
  mounted() {
    this.renderChart();
    window.addEventListener('resize', this.renderChart);
  },
  
  watch: {
    chartConfig: {
      handler(newConfig) {
        this.lastUpdated = newConfig.last_updated
          ? new Date(newConfig.last_updated).toLocaleString()
          : new Date().toLocaleString();
        this.renderChart();
      },
      immediate: true,
      deep: true
    }
  },
  
  beforeUnmount() {
    window.removeEventListener('resize', this.renderChart);
  },
  
  methods: {
    renderChart() {
      const chartEl = this.$refs.chart;
      if (!chartEl) {
        console.error('無法取得圖表的引用（chartEl）');
        return;
      }

      // 檢查圖表配置是否存在
      if (!this.chartConfig) {
        console.error('圖表配置未定義');
        return;
      }

      const color = (this.chartConfig.color && this.chartConfig.color.hex) || '#000000';
      const colorPalette = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
      ];

      let data = [];
      const layout = {
        title: this.chartConfig.name || '圖表',
        xaxis: {
          title: this.chartConfig.xAxisField || 'X 軸',
          tickangle: -90,
          automargin: true
        },
        yaxis: {
          title: this.chartConfig.yAxisField || 'Y 軸'
        },
        autosize: true,
      };

      // 根據圖表類型創建適當的數據結構
      try {
        switch (this.chartConfig.chartType) {
          case 'multi_line': {
            let traces = [];
            const x_data = this.chartConfig.x_data || [];
            const y_data = this.chartConfig.y_data || {};
            
            if (Array.isArray(x_data) && typeof y_data === 'object') {
              let colorIndex = 0;
              for (const [y_field, y_values] of Object.entries(y_data)) {
                if (Array.isArray(y_values)) {
                  traces.push({
                    x: x_data,
                    y: y_values,
                    type: 'scatter',
                    mode: 'lines',
                    name: y_field,
                    line: { color: colorPalette[colorIndex % colorPalette.length] },
                  });
                  colorIndex++;
                }
              }
              data = traces;
            }
            break;
          }

          case 'combo': {
            if (Array.isArray(this.chartConfig.x_data) &&
                Array.isArray(this.chartConfig.y_data_bar) &&
                Array.isArray(this.chartConfig.y_data_line)) {
              const trace1 = {
                x: this.chartConfig.x_data,
                y: this.chartConfig.y_data_bar,
                type: 'bar',
                name: this.chartConfig.y_field_bar || '柱狀圖數據',
                marker: { color: colorPalette[0] },
                yaxis: 'y1',
              };
              const trace2 = {
                x: this.chartConfig.x_data,
                y: this.chartConfig.y_data_line,
                type: 'scatter',
                mode: 'lines+markers',
                name: this.chartConfig.y_field_line || '折線圖數據',
                line: { color: colorPalette[1] },
                yaxis: 'y2',
              };
              data = [trace1, trace2];
              layout.yaxis2 = {
                title: this.chartConfig.y_field_line || 'Y 軸',
                overlaying: 'y',
                side: 'right',
              };
            }
            break;
          }

          case 'treemap': {
            if (Array.isArray(this.chartConfig.labels) && 
                Array.isArray(this.chartConfig.values) && 
                Array.isArray(this.chartConfig.parents)) {
              data = [{
                type: 'treemap',
                labels: this.chartConfig.labels,
                parents: this.chartConfig.parents,
                values: this.chartConfig.values,
                textinfo: "label+value",
                marker: {
                  colors: colorPalette.slice(0, this.chartConfig.labels.length || 0)
                }
              }];
            } else {
              console.error('Treemap 所需的數據格式不正確');
            }
            break;
          }

          case 'donut': {
            if (Array.isArray(this.chartConfig.labels) && 
                Array.isArray(this.chartConfig.values)) {
              data = [{
                type: 'pie',
                labels: this.chartConfig.labels,
                values: this.chartConfig.values,
                hole: 0.4,
                marker: {
                  colors: colorPalette.slice(0, this.chartConfig.labels.length || 0)
                }
              }];
            } else {
              console.error('Donut 所需的數據格式不正確');
            }
            break;
          }

          case 'funnel': {
            if (Array.isArray(this.chartConfig.labels) && 
                Array.isArray(this.chartConfig.values)) {
              data = [{
                type: 'funnel',
                y: this.chartConfig.labels,
                x: this.chartConfig.values,
                textinfo: "value+percent",
                marker: {
                  colors: colorPalette.slice(0, this.chartConfig.labels.length || 0)
                }
              }];
            } else {
              console.error('Funnel 所需的數據格式不正確');
            }
            break;
          }

          case 'horizontal_bar': {
            if (Array.isArray(this.chartConfig.x_data) && 
                Array.isArray(this.chartConfig.y_data)) {
              let marker = { color: color };
              if (this.chartConfig.threshold != null) {
                const colors = this.chartConfig.y_data.map(value => 
                  value >= this.chartConfig.threshold ? 'red' : 'blue'
                );
                marker = { color: colors };
              }
              data = [{
                x: this.chartConfig.x_data,
                y: this.chartConfig.y_data,
                type: 'bar',
                orientation: 'h',
                marker: marker,
              }];
            }
            break;
          }

          case 'pie': {
            if (Array.isArray(this.chartConfig.x_data) && 
                Array.isArray(this.chartConfig.y_data)) {
              data = [{
                labels: this.chartConfig.x_data,
                values: this.chartConfig.y_data,
                type: 'pie',
                marker: {
                  colors: colorPalette.slice(0, this.chartConfig.x_data.length || 0)
                }
              }];
            }
            break;
          }

          default: {
            // 處理基本圖表類型（bar, line 等）
            if (Array.isArray(this.chartConfig.x_data) && 
                Array.isArray(this.chartConfig.y_data)) {
              let marker = { color: color };
              if (this.chartConfig.threshold != null) {
                const colors = this.chartConfig.y_data.map(value => 
                  value >= this.chartConfig.threshold ? 'red' : 'blue'
                );
                marker = { color: colors };
              }

              data = [{
                x: this.chartConfig.x_data,
                y: this.chartConfig.y_data,
                type: this.chartConfig.chartType || 'bar',
                marker: marker,
                line: { color: color },
              }];
            }
          }
        }

        // 只有在有效數據時才渲染圖表
        if (data.length > 0) {
          Plotly.newPlot(chartEl, data, layout, {
            displaylogo: false,
            responsive: true,
            modeBarButtonsToRemove: ['select2d', 'lasso2d', 'autoScale2d']
          });
        } else {
          console.error('沒有有效的圖表數據可供渲染');
        }
      } catch (error) {
        console.error('渲染圖表時發生錯誤:', error);
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