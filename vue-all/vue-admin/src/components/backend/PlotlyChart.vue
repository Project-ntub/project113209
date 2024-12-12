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
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
        '#b71c1c', '#0d47a1', '#1b5e20', '#f57f17', '#4a148c',
        '#006064', '#bf360c', '#33691e', '#3e2723', '#880e4f'
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

          case 'donut': {
              if (this.chartConfig.x_data && this.chartConfig.y_data) {
                  data = [{
                      type: 'pie',
                      labels: this.chartConfig.x_data,
                      values: this.chartConfig.y_data,
                      hole: 0.6,  // 加大中間空心
                      textposition: 'outside',  // 文字標籤放在外面
                      textinfo: "label+percent",
                      hoverinfo: "label+value+percent",
                      pull: 0.02,  // 輕微分離各個扇形
                      marker: {
                          colors: colorPalette,
                          line: {
                              color: 'white',
                              width: 2
                          }
                      },
                      insidetextorientation: 'radial'  // 放射狀的文字方向
                  }];

                  // 在中間添加總計數值
                  const total = this.chartConfig.y_data.reduce((a, b) => a + b, 0);
                  layout.annotations = [{
                      font: {
                          size: 20,
                          color: '#333'
                      },
                      showarrow: false,
                      text: `總計<br>${total.toLocaleString('zh-TW')}`,
                      x: 0.5,
                      y: 0.5
                  }];

                  layout.showlegend = true;
                  layout.height = 500;
                  layout.legend = {
                      orientation: 'h',
                      y: -0.2,
                      x: 0.5,
                      xanchor: 'center'
                  };
              }
              break;
          }

          // case 'funnel': {
          //     if (this.chartConfig.x_data && this.chartConfig.y_data) {
          //         data = [{
          //             type: 'funnel',
          //             y: this.chartConfig.x_data,  // 使用名稱作為Y軸
          //             x: this.chartConfig.y_data,   // 使用數值作為X軸
          //             textposition: "inside",
          //             textinfo: "value+percent initial",
          //             opacity: 0.85,
          //             marker: {
          //                 color: colorPalette,
          //                 line: {
          //                     width: 2,
          //                     color: 'white'
          //                 }
          //             },
          //             connector: {
          //                 line: {
          //                     color: "royalblue",
          //                     width: 1
          //                 }
          //             },
          //             hoverinfo: 'name+percent previous+percent total',
          //         }];

          //         // 專業的漏斗圖布局
          //         layout.showlegend = true;
          //         layout.height = 600;
          //         layout.margin = { l: 150, r: 0, b: 0, t: 30, pad: 4 };
          //         layout.funnelmode = "stack";
          //         layout.legend = {
          //             orientation: 'h',
          //             y: -0.2
          //         };
          //     }
          //     break;
          // }

          // case 'horizontal_bar': {
          //   if (Array.isArray(this.chartConfig.x_data) && 
          //       Array.isArray(this.chartConfig.y_data)) {
          //     let marker = { color: color };
          //     if (this.chartConfig.threshold != null) {
          //       const colors = this.chartConfig.y_data.map(value => 
          //         value >= this.chartConfig.threshold ? 'red' : 'blue'
          //       );
          //       marker = { color: colors };
          //     }
          //     data = [{
          //       x: this.chartConfig.x_data,
          //       y: this.chartConfig.y_data,
          //       type: 'bar',
          //       orientation: 'h',
          //       marker: marker,
          //     }];
          //   }
          //   break;
          // }

          case 'bar':
          case 'horizontal_bar': {
            if (Array.isArray(this.chartConfig.x_data) && 
                Array.isArray(this.chartConfig.y_data)) {
              
              // 獲取極值
              const { highest, lowest } = this.getExtremeValues(this.chartConfig.y_data, 3);
              const extremeIndices = [...highest, ...lowest].map(item => item.index);
              
              // 生成顏色數組
              const colors = this.chartConfig.y_data.map((value, index) => {
                if (highest.some(h => h.index === index)) {
                  return '#FF4136'; // 高值用紅色
                } else if (lowest.some(l => l.index === index)) {
                  return '#0074D9'; // 低值用藍色
                }
                return color; // 其他用默認顏色
              });

              const trace = {
                x: this.chartConfig.chartType === 'horizontal_bar' ? this.chartConfig.x_data : this.chartConfig.x_data,
                y: this.chartConfig.chartType === 'horizontal_bar' ? this.chartConfig.x_data : this.chartConfig.y_data,
                type: 'bar',
                orientation: this.chartConfig.chartType === 'horizontal_bar' ? 'h' : 'v',
                marker: {
                  color: colors,
                  line: {
                    color: 'white',
                    width: 1
                  }
                },
                text: this.chartConfig.y_data.map((value, index) => {
                  if (extremeIndices.includes(index)) {
                    return value.toLocaleString('zh-TW');
                  }
                  return '';
                }),
                textposition: 'outside',
                hovertemplate: '%{y}: %{x}<extra></extra>'
              };

              data = [trace];

              // 為極值添加標註
              layout.annotations = [
                ...highest.map(({ value, index }) => ({
                  x: this.chartConfig.chartType === 'horizontal_bar' ? value : this.chartConfig.x_data[index],
                  y: this.chartConfig.chartType === 'horizontal_bar' ? this.chartConfig.x_data[index] : value,
                  text: '🔺',
                  showarrow: false,
                  font: { size: 16 },
                  yshift: this.chartConfig.chartType === 'horizontal_bar' ? 0 : 20,
                  xshift: this.chartConfig.chartType === 'horizontal_bar' ? 20 : 0
                })),
                ...lowest.map(({ value, index }) => ({
                  x: this.chartConfig.chartType === 'horizontal_bar' ? value : this.chartConfig.x_data[index],
                  y: this.chartConfig.chartType === 'horizontal_bar' ? this.chartConfig.x_data[index] : value,
                  text: '🔻',
                  showarrow: false,
                  font: { size: 16 },
                  yshift: this.chartConfig.chartType === 'horizontal_bar' ? 0 : -20,
                  xshift: this.chartConfig.chartType === 'horizontal_bar' ? -20 : 0
                }))
              ];
            }
            break;
          }

          case 'pie': {
              if (this.chartConfig.x_data && this.chartConfig.y_data) {
                  data = [{
                      type: 'pie',
                      labels: this.chartConfig.x_data,
                      values: this.chartConfig.y_data,
                      hole: 0,  // 無空心
                      textposition: 'inside',  // 文字標籤放在內部
                      textinfo: "percent",  // 只顯示百分比
                      hoverinfo: "label+value+percent",
                      marker: {
                          colors: colorPalette,
                          line: {
                              color: 'white',
                              width: 1
                          }
                      }
                  }];

                  layout.showlegend = true;
                  layout.height = 450;
                  layout.legend = {
                      orientation: 'v',
                      y: 1,
                      x: 1.1
                  };
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
    },
    getExtremeValues(values, count = 3) {
      if (!Array.isArray(values) || values.length === 0) return { highest: [], lowest: [] };
      
      // 創建帶索引的數組
      const indexed = values.map((value, index) => ({ value, index }));
      
      // 排序
      const sorted = [...indexed].sort((a, b) => b.value - a.value);
      
      // 獲取最高和最低的幾個值
      const highest = sorted.slice(0, count);
      const lowest = sorted.slice(-count).reverse();
      
      return { highest, lowest };
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