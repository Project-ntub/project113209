<template>
  <ChartContainer>
    <div class="chart-wrapper">
      <div class="chart-inner">
        <canvas ref="chartCanvas"></canvas>
      </div>
    </div>
  </ChartContainer>
</template>
<script>
import { Chart as ChartJS, LineController, LineElement, PointElement, LinearScale, Title, Tooltip, Legend, CategoryScale } from 'chart.js';
import ChartContainer from '@/Charts/ChartContainer.vue';  // 引入通用容器组件

ChartJS.register(LineController, LineElement, PointElement, LinearScale, Title, Tooltip, Legend, CategoryScale);

export default {
  name: 'SalesChart',
  components: {
    ChartContainer
  },
  data() {
    return {
      chartData: {
        labels: ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
        datasets: [
          {
            label: 'Sales',
            backgroundColor: '#f87979',
            data: [40, 20, 12, 39, 10, 40, 39, 80, 40, 39, 80, 40]
          }
        ]
      },
      chartOptions: {
        plugins: {
          tooltip: {
            backgroundColor: '#007bff', // 工具提示背景改為藍色
            titleColor: '#ffffff', // 標題顏色改為白色
            bodyColor: '#ffffff'  // 內容顏色改為白色
          },
          legend: {
            labels: {
              color: '#007bff', // 圖例標籤顏色改為藍色
              fontSize: 8 // 縮小圖例字體大小
            }
          }
        },
        scales: {
          x: {
            ticks: {
              font: {
                size: 6 // 縮小x軸字體大小
              }
            }
          },
          y: {
            ticks: {
              font: {
                size: 6 // 縮小y軸字體大小
              }
            }
          }
        },
        responsive: true,
        maintainAspectRatio: false
      }
    };
  },
  methods: {
    renderChart() {
      const ctx = this.$refs.chartCanvas.getContext('2d');
      this.chartInstance = new ChartJS(ctx, {
        type: 'line',
        data: this.chartData,
        options: this.chartOptions
      });
    }
  },
  mounted() {
    this.renderChart();
  }
};
</script>
<style scoped>
.resizable-container {
  resize: both;
  overflow: auto;
  aspect-ratio: 16/9;
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.1);
  margin-left: auto;
  margin-right: auto;
  display: block;
  width: 320px; /* 調大初始寬度 */
  height: 180px; /* 調大初始高度 */
}

.chart-inner {
  width: 100%;
  height: 100%;
  padding: 8px;
}

canvas {
  width: 100% !important;
  height: 100% !important;
  aspect-ratio: inherit;
}

/* 手機螢幕 */
@media (max-width: 480px) {
  .resizable-container {
    width: 250px;
    height: auto;
  }

  .chart-inner {
    padding: 4px;
  }
}

/* 平板 */
@media (min-width: 481px) and (max-width: 1024px) {
  .resizable-container {
    width: 280px;
    height: auto;
  }

  .chart-inner {
    padding: 6px;
  }
}

/* 桌面設備 */
@media (min-width: 1025px) {
  .resizable-container {
    width: 400px; /* 桌面版保持較大寬度 */
    height: 225px; /* 桌面版保持較大高度 */
  }

  .chart-inner {
    padding: 10px;
  }
}
</style>

