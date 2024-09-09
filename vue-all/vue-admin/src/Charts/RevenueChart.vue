<template>
  <ChartContainer>
    <div class="resizable-container">
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
  name: 'RevenueChart',
  components: {
    ChartContainer
  },
  data() {
    return {
      chartData: {
        labels: ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
        datasets: [
          {
            label: 'Revenue',
            backgroundColor: '#f87979',
            data: [30, 10, 5, 25, 15, 30, 25, 60, 30, 25, 60, 30]
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
        maintainAspectRatio: false // 不保持原比例
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
  resize: both; /* 允许拖动 */
  overflow: auto; /* 自动溢出 */
  aspect-ratio: 16/9; /* 保持容器的宽高比 */
  background-color: #f8f9fa; /* 白邊顏色 */
  border-radius: 8px;
  box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.1);
  margin-left: auto;
  margin-right: auto;
  display: block; /* 确保块级显示，以使resize生效 */
  width: 220px; /* 默认宽度 */
  height: auto; /* 自动高度 */
}

.chart-inner {
  width: 100%;
  height: 100%;
  padding: 8px;
}

canvas {
  width: 100% !important;
  height: 100% !important;
  aspect-ratio: inherit; /* 保持 canvas 的宽高比 */
}

/* 超小屏幕 (如手机) */
@media (max-width: 480px) {
  .resizable-container {
    width: 200px;
    height: auto;
  }

  .chart-inner {
    padding: 4px;
  }
}

/* 小型设备 (如小平板) */
@media (min-width: 481px) and (max-width: 768px) {
  .resizable-container {
    width: 200px;
    height: auto;
  }

  .chart-inner {
    padding: 6px;
  }
}

/* 中型设备 (如大平板) */
@media (min-width: 769px) and (max-width: 1024px) {
  .resizable-container {
    width: 200px;
    height: auto;
  }

  .chart-inner {
    padding: 6px;
  }
}

/* 大型设备 (如桌面) */
@media (min-width: 1025px) {
  .resizable-container {
    width: 220px;
    height: auto;
  }

  .chart-inner {
    padding: 8px;
  }
}
</style>
