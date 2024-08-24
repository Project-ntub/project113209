<template>
  <div>
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script>
import { Chart as ChartJS, Title, Tooltip, Legend, LineController, LineElement, PointElement, LinearScale, CategoryScale } from 'chart.js'
ChartJS.register(Title, Tooltip, Legend, LineController, LineElement, PointElement, LinearScale, CategoryScale)

export default {
  name: 'SalesChart',
  data() {
    return {
      // 定义图表数据
      chartData: {
        labels: ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
        datasets: [
          {
            label: 'Sales',
            backgroundColor: '#f87979',
            data: [40, 20, 12, 39, 10, 40, 39, 80, 40, 39, 80, 40]
          }
        ]
      }
    };
  },
  mounted() {
    this.renderChart()
  },
  methods: {
    // 渲染图表
    renderChart() {
      const ctx = this.$refs.chartCanvas.getContext('2d')
      new ChartJS(ctx, {
        type: 'line',
        data: this.chartData,
        options: { 
          responsive: true, 
          maintainAspectRatio: false 
        }
      })
    }
  }
}
</script>

<style scoped>
canvas {
  width: 100% !important; /* 默认占据容器的全部宽度 */
  height: 400px !important; /* 默认高度为400px */
}

/* 超小屏幕 (如手机) */
@media (max-width: 480px) {
  canvas {
    height: 250px !important; /* 在小屏幕上减少高度 */
    margin-left: 0px !important;
  }
}

/* 小型设备 (如小平板) */
@media (min-width: 481px) and (max-width: 768px) {
  canvas {
    height: 300px !important; /* 小平板设备的高度适中 */
  }
}

/* 中型设备 (如大平板) */
@media (min-width: 769px) and (max-width: 1024px) {
  canvas {
    height: 350px !important; /* 大平板设备的高度适中 */
  }
}

/* 大型设备 (如桌面) */
@media (min-width: 1025px) {
  canvas {
    height: 400px !important; /* 在桌面上恢复默认高度 */
  }
}
</style>
