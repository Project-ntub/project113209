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
            data: [50, 25, 18, 45, 20, 50, 45, 100, 50, 45, 100, 50],
          },
        ],
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
  mounted() {
    this.renderChart();
  },
  methods: {
    renderChart() {
      const ctx = this.$refs.chartCanvas.getContext('2d');
      this.chartInstance = new ChartJS(ctx, {
        type: 'line', // 使用折線圖
        data: this.chartData,
        options: this.chartOptions,
      });
    }
  }
};
</script>

<style scoped>
.chart-wrapper {
  width: 100%;
  max-width: 220px; /* 容器宽度 */
  max-height: 120px; /* 容器高度 */
  overflow: hidden; /* 确保内容不溢出 */
  background-color: #f8f9fa; /* 背景颜色 */
  padding: 8px; /* 内边距 */
  border-radius: 8px; /* 圆角效果 */
  box-shadow: 0px 0px 5px rgba(0, 0, 0, 0.1); /* 阴影效果 */
  margin-left: auto;
  margin-right: auto; /* 居中显示 */
}

/* 超小屏幕 (如手机) */
@media (max-width: 480px) {
  .chart-wrapper {
    max-width: 200px; /* 小屏幕宽度 */
    max-height: 100px; /* 小屏幕高度 */
    padding: 4px; /* 小屏幕内边距 */
  }
}

/* 小型设备 (如小平板) */
@media (min-width: 481px) and (max-width: 768px) {
  .chart-wrapper {
    max-width: 200px; /* 小平板宽度 */
    max-height: 100px; /* 小平板高度 */
    padding: 6px; /* 小平板内边距 */
  }
}

/* 中型设备 (如大平板) */
@media (min-width: 769px) and (max-width: 1024px) {
  .chart-wrapper {
    max-width: 200px; /* 大平板宽度 */
    max-height: 100px; /* 大平板高度 */
    padding: 6px; /* 大平板内边距 */
  }
}

/* 大型设备 (如桌面) */
@media (min-width: 1025px) {
  .chart-wrapper {
    max-width: 220px; /* 桌面设备宽度 */
    max-height: 120px; /* 桌面设备高度 */
    padding: 8px; /* 桌面设备内边距 */
  }
}
</style>
