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
      chartInstance: null,
    };
  },
  methods: {
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
    this.renderChart();
  }
};
</script>

<style scoped>
canvas {
  width: 100% !important;
  height: 100% !important; /* 使用百分比以確保圖表隨容器縮放 */
}
</style>
