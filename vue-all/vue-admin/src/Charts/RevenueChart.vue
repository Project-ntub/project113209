<template>
  <div ref="chartComponent">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script>
import { Chart as ChartJS, Title, Tooltip, Legend, LineController, LineElement, PointElement, LinearScale, CategoryScale } from 'chart.js';
ChartJS.register(Title, Tooltip, Legend, LineController, LineElement, PointElement, LinearScale, CategoryScale);

export default {
  name: 'RevenueChart',
  data() {
    return {
      chartData: {
        labels: ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'],
        datasets: [
          {
            label: 'Revenue',
            backgroundColor: '#f87979',
            data: [50, 25, 18, 45, 20, 50, 45, 100, 50, 45, 100, 50]
          }
        ]
      }
    };
  },
  mounted() {
    this.renderChart();
  },
  methods: {
    renderChart() {
      const ctx = this.$refs.chartCanvas.getContext('2d');
      new ChartJS(ctx, {
        type: 'line',
        data: this.chartData,
        options: { responsive: true, maintainAspectRatio: false }
      });
    }
  }
};
</script>

<style scoped>
canvas {
  width: 100% !important;
  height: 400px !important;
}
</style>
