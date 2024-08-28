<template>
  <ChartContainer>
    <canvas ref="chartCanvas"></canvas>
  </ChartContainer>
</template>

<script>
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, LineElement, PointElement, LinearScale, CategoryScale, ArcElement } from 'chart.js';
import ChartContainer from '@/Charts/ChartContainer.vue';

ChartJS.register(Title, Tooltip, Legend, BarElement, LineElement, PointElement, LinearScale, CategoryScale, ArcElement);

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
        options: { responsive: true, maintainAspectRatio: false },
      });
    },
  },
};
</script>

<style scoped>
canvas {
  width: 700px !important;
  height: 400px !important;
}
</style>
