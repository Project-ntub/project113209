<template>
  <ChartContainer>
    <canvas ref="chartCanvas"></canvas>
  </ChartContainer>
</template>

<script>
import { Chart as ChartJS, RadarController, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend } from 'chart.js';
import ChartContainer from '@/Charts/ChartContainer.vue';

ChartJS.register(RadarController, PointElement, LinearScale, CategoryScale, Title, Tooltip, Legend);

export default {
  name: 'RevenueChart',
  components: {
    ChartContainer
  },
  data() {
    return {
      // 定义图表数据
      chartData: {
        labels: ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
        datasets: [
          {
            label: 'Revenue',
            backgroundColor: '#f87979',
            data: [30, 10, 5, 25, 15, 30, 25, 60, 30, 25, 60, 30]
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
        options: { responsive: true, maintainAspectRatio: false }
      })
    }
  }
}
</script>

<style scoped>
canvas {
  width: 700px !important;
  height: 400px !important;
}
</style>
