<template>
  <ChartContainer>
    <div class="chart-wrapper">
      <canvas ref="chartCanvas"></canvas>
    </div>
  </ChartContainer>
</template>

<script>
import { Chart as ChartJS, Title, Tooltip, Legend, LineController, LineElement, PointElement, LinearScale, CategoryScale, BarElement, ArcElement } from 'chart.js';
import ChartContainer from '@/Charts/ChartContainer.vue';

ChartJS.register(Title, Tooltip, Legend, LineController, LineElement, PointElement, LinearScale, CategoryScale, BarElement, ArcElement);


export default {
  name: 'InventoryChart',
  components: {
    ChartContainer
  },
  data() {
    return {
      chartData: {
        labels: ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
        datasets: [
          {
            label: 'Inventory',
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
  mounted() {
    this.renderChart();
  },
  methods: {
    renderChart() {
      const ctx = this.$refs.chartCanvas.getContext('2d');
      this.chartInstance = new ChartJS(ctx, {
        type: 'line', // 使用折線圖
        data: this.chartData,
        options: this.chartOptions
      });
    }
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