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
  methods: {
    // 渲染图表
      renderChart() {
      const ctx = this.$refs.chartCanvas.getContext('2d');
      this.chartInstance = new ChartJS(ctx, {
        type: 'line', // 根據需要調整類型
        data: this.chartData,
        options: { 
          responsive: true, 
          maintainAspectRatio: false 
        },
      });
    }
  },
  mounted() {
    this.renderChart()
  },
}
</script>

<style scoped>
canvas {
  width: 100% !important;
  height: 100% !important; /* 使用百分比以確保圖表隨容器縮放 */
}
</style>
