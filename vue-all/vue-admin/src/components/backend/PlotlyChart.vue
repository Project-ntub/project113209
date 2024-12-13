<template>
  <!-- 圖表容器，使用 Plotly 渲染 -->
  <div ref="chart" class="plotly-chart" @click.stop></div>
  <!-- 顯示最後更新時間 -->
  <div class="last-updated">最後更新時間: {{ lastUpdated }}</div>
</template>

<script>
import Plotly from 'plotly.js-dist';

export default {
  // 接收圖表配置作為屬性
  props: ['chartConfig'],
  
  data() {
    return {
      lastUpdated: ''
    };
  },
  
  // 組件掛載時初始化圖表
  mounted() {
    this.renderChart();
    // 監聽視窗大小變化，實現響應式設計
    window.addEventListener('resize', this.renderChart);
  },
  
  // 監聽配置變化，更新圖表
  watch: {
    chartConfig: {
      handler(newConfig) {
        // 更新最後更新時間
        this.lastUpdated = newConfig.last_updated
          ? new Date(newConfig.last_updated).toLocaleString()
          : new Date().toLocaleString();
        this.renderChart();
      },
      immediate: true,
      deep: true
    }
  },
  
  // 組件卸載時清理事件監聽
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

      if (!this.chartConfig) {
        console.error('圖表配置未定義');
        return;
      }

      // 定義顏色配置
      const color = (this.chartConfig.color && this.chartConfig.color.hex) || '#000000';
      const colorPalette = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
        '#b71c1c', '#0d47a1', '#1b5e20', '#f57f17', '#4a148c',
        '#006064', '#bf360c', '#33691e', '#3e2723', '#880e4f'
      ];

      // 初始化數據和布局配置
      let data = [];
      const layout = {
        title: this.chartConfig.name || '圖表',
        xaxis: {
          title: this.chartConfig.xAxisField || 'X 軸',
          tickangle: -45,
          automargin: true,
          textposition: 'inside',    
          tickfont: {
            size: 10  // 調整字體大小
          },
          ticktext: this.chartConfig.x_data.map(text => {
            // 若文字過長則截斷
            return text.length > 15 ? text.substr(0, 15) + '...' : text;
          }),
          tickvals: [...Array(this.chartConfig.x_data.length).keys()]
        },
        yaxis: {
          title: this.chartConfig.yAxisField || 'Y 軸',
          automargin: true,
          size: 10,
        },
        margin: {
          l: 80,   // 左邊距
          r: 50,   // 右邊距
          b: 50,  // 底部邊距，為長標籤留空間
          t: 100    // 頂部邊距
        },
        // height: Math.max(500, this.chartConfig.y_data.length * 30),
        autosize: true,
      };

      try {
        switch (this.chartConfig.chartType) {
          case 'bar': {
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
                return color; // 其他用預設藍色
              });

              const trace = {
                x: this.chartConfig.x_data,
                y: this.chartConfig.y_data,
                type: 'bar',
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
                textposition: 'outside'
              };

              data = [trace];

              // 添加極值標註
              layout.annotations = [
                ...highest.map(({ value, index }) => ({
                  x: this.chartConfig.x_data[index],
                  y: value,
                  text: '🔺',
                  showarrow: false,
                  font: { size: 16 },
                  yshift: 20
                })),
                ...lowest.map(({ value, index }) => ({
                  x: this.chartConfig.x_data[index],
                  y: value,
                  text: '🔻',
                  showarrow: false,
                  font: { size: 16 },
                  yshift: -20
                }))
              ];
            }
            break;
          }

          // 多線圖表處理
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

          // 組合圖表處理
          case 'combo': {
            if (Array.isArray(this.chartConfig.x_data) &&
                Array.isArray(this.chartConfig.y_data_bar) &&
                Array.isArray(this.chartConfig.y_data_line)) {
              const trace1 = {
                x: this.chartConfig.x_data,
                y: this.chartConfig.y_data_bar,
                type: 'bar',
                name: this.chartConfig.y_field_bar || '直條圖數據',
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

          // 環形圖處理
          case 'donut': {
            if (this.chartConfig.x_data && this.chartConfig.y_data) {
              data = [{
                type: 'pie',
                labels: this.chartConfig.x_data,
                values: this.chartConfig.y_data,
                hole: 0.6,  // 中間空心比例
                textposition: 'outside',  // 文字標籤位置
                textinfo: "label+percent",
                hoverinfo: "label+value+percent",
                pull: 0.02,  // 扇形分離距離
                marker: {
                  colors: colorPalette,
                  line: {
                    color: 'white',
                    width: 2
                  }
                },
                insidetextorientation: 'radial'  // 內部文字方向
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

          // 橫向條形圖處理
          case 'horizontal_bar': {
            if (Array.isArray(this.chartConfig.x_data) && 
                Array.isArray(this.chartConfig.y_data)) {
              
              // 獲取極值並計算顏色
              const values = this.chartConfig.x_data;
              const { highest, lowest } = this.getExtremeValues(values, 3);
              const extremeIndices = [...highest, ...lowest].map(item => item.index);
              
              // 生成顏色數組
              const colors = values.map((value, index) => {
                if (highest.some(h => h.index === index)) {
                  return '#FF4136'; // 高值用紅色
                } else if (lowest.some(l => l.index === index)) {
                  return '#0074D9'; // 低值用藍色
                }
                return color; 
              });

              const trace = {
                x: this.chartConfig.x_data,           // 數量作為 X 軸
                y: this.chartConfig.y_data,           // 產品名稱作為 Y 軸
                type: 'bar',
                orientation: 'h',                     // 設置為橫向
                marker: {
                  color: colors,
                  line: {
                    color: 'white',
                    width: 1
                  }
                },
                // 添加數據標籤
                text: this.chartConfig.x_data.map((value, index) => {
                  if (extremeIndices.includes(index)) {
                    return value.toLocaleString('zh-TW');
                  }
                  return '';
                }),
                textposition: 'outside',
                hovertemplate: '%{y}: %{x}<extra></extra>'
              };

              data = [trace];

              // 調整布局
              layout.margin = {
                l: 150,  // 加大左邊距以容納產品名稱
                r: 50,
                t: 50,
                b: 50
              };
              
              // 修改座標軸標題
              layout.xaxis.title = '庫存數量';
              layout.yaxis.title = '';  // 移除 Y 軸標題
              
              // 確保圖表高度足夠
              layout.height = Math.max(500, this.chartConfig.y_data.length * 30);
              layout.autosize = true;

              // 為極值添加標註
              layout.annotations = [
                ...highest.map(({ value, index }) => ({
                  x: value,
                  y: this.chartConfig.y_data[index],
                  text: '🔺',
                  showarrow: false,
                  font: { size: 16 },
                  xshift: 20,
                  yshift: 0
                })),
                ...lowest.map(({ value, index }) => ({
                  x: value,
                  y: this.chartConfig.y_data[index],
                  text: '🔻',
                  showarrow: false,
                  font: { size: 16 },
                  xshift: -20,
                  yshift: 0
                }))
              ];
            }
            break;
          }

          // 圓餅圖處理
          case 'pie': {
            if (this.chartConfig.x_data && this.chartConfig.y_data) {
              data = [{
                type: 'pie',
                labels: this.chartConfig.x_data,
                values: this.chartConfig.y_data,
                hole: 0,  // 無空心
                textposition: 'inside',  // 文字標籤在內部
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

          case 'area': {
            data = [{
              x: this.chartConfig.x_data,
              y: this.chartConfig.y_data,
              type: 'scatter',
              fill: 'tozeroy',
              line: {
                color: '#4a90e2'
              }
            }];
            break;
          }

          case 'grouped_bar': {
            // 需要修改後端 API 以支持分組數據
            const traces = categories.map((category, i) => ({
              name: category,
              x: this.chartConfig.x_data,
              y: this.chartConfig.y_data[i],
              type: 'bar',
              marker: {
                color: colorPalette[i]
              }
            }));
            data = traces;
            layout.barmode = 'group';
            break;
          }

          // 一般圖表處理（柱狀圖、折線圖等）
          default: {
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

        // 只在有效數據時渲染圖表
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

    // 獲取數據中的極值（最高和最低值）
    getExtremeValues(values, count = 3) {
      if (!Array.isArray(values) || values.length === 0) {
        return { highest: [], lowest: [] };
      }
      
      // 創建帶索引的數組
      const indexed = values.map((value, index) => ({ value, index }));
      
      // 排序並獲取最高和最低值
      const sorted = [...indexed].sort((a, b) => b.value - a.value);
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
  min-height: 400px;
}
.last-updated {
  margin-top: 10px;
  font-size: 12px;
  color: #555;
  text-align: right;
}
</style>