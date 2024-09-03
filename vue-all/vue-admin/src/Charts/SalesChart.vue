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
  },
}
</script>

<style scoped>
.chart-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 220px;  /* 白邊包住圖的寬度 */
  height: 120px; /* 白邊包住圖的高度 */
  background-color: #f8f9fa; /* 白邊顏色 */
  border-radius: 8px;
  box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.1);
  margin-left: auto;
  margin-right: auto;
}

.chart-inner {
  width: 100%;
  height: 100%;
  padding: 8px;
}

/* 超小屏幕 (如手机) */
@media (max-width: 480px) {
  .chart-wrapper {
    width: 200px;
    height: 100px;
  }

  .chart-inner {
    padding: 4px;
  }
}

/* 小型设备 (如小平板) */
@media (min-width: 481px) and (max-width: 768px) {
  .chart-wrapper {
    width: 200px;
    height: 100px;
  }

  .chart-inner {
    padding: 6px;
  }
}

/* 中型设备 (如大平板) */
@media (min-width: 769px) and (max-width: 1024px) {
  .chart-wrapper {
    width: 200px;
    height: 100px;
  }

  .chart-inner {
    padding: 6px;
  }
}

/* 大型设备 (如桌面) */
@media (min-width: 1025px) {
  .chart-wrapper {
    width: 220px;
    height: 120px;
  }

  .chart-inner {
    padding: 8px;
  }
}
</style>
