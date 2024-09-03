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
            label: 'SalesChart',
            backgroundColor: '#f87979',
            data: [50, 25, 18, 45, 20, 50, 45, 100, 50, 45, 100, 50]
          }
        ]
      },
      chartOptions: {
        plugins: {
          tooltip: {
            backgroundColor: '#007bff', // 工具提示背景改為藍色
            titleColor: '#ffffff', // 標題顏色改為白色
            bodyColor: '#ffffff',  // 內容顏色改為白色
          },
          legend: {
            labels: {
              color: '#007bff', // 圖例標籤顏色改為藍色
              fontSize: 8, // 縮小圖例字體大小
            }
          }
        },
        scales: {
          x: {
            ticks: {
              font: {
                size: 6, // 縮小x軸字體大小
              }
            }
          },
          y: {
            ticks: {
              font: {
                size: 6, // 縮小y軸字體大小
              }
            }
          }
        },
        responsive: true,
        maintainAspectRatio: false,
      }
    };
  },
  methods: {
    renderChart() {
      const ctx = this.$refs.chartCanvas.getContext('2d');
      this.chartInstance = new ChartJS(ctx, {
        type: 'line',
        data: this.chartData,
        options: this.chartOptions,
      });
    }
  },
  mounted() {
    this.renderChart();
  }
}
</script>

<style scoped>
.chart-wrapper {
  width: 100%; /* 容器寬度占滿父級 */
  max-height: 400px; /* 設置最大高度以啟用滾動條 */
  overflow: auto; /* 啟用滾動條 */
}

canvas {
  width: 100% !important; /* 默認占據容器的全部寬度 */
  height: 100% !important; /* 高度設為100%以適應容器 */
}

/* 響應式設計 */
@media (max-width: 480px) {
  .chart-wrapper {
    max-height: 250px !important; /* 在小屏幕上減少最大高度 */
  }

  canvas {
    height: auto !important; /* 確保 canvas 高度自動適應容器 */
  }
}

@media (min-width: 481px) and (max-width: 768px) {
  .chart-wrapper {
    max-height: 300px !important; /* 小平板設備的最大高度適中 */
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .chart-wrapper {
    max-height: 350px !important; /* 大平板設備的最大高度適中 */
  }
}

@media (min-width: 1025px) {
  .chart-wrapper {
    max-height: 400px !important; /* 在桌面上恢復默認最大高度 */
  }
}
</style>
