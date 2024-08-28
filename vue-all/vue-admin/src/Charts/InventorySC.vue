<template>
  <ChartContainer>
    <canvas ref="chartCanvas"></canvas>
  </ChartContainer>
</template>

<script>
import { 
  Chart as ChartJS, 
  RadarController, 
  PointElement, 
  RadialLinearScale, // 正確匯入 RadialLinearScale
  CategoryScale, 
  Title, 
  Tooltip, 
  Legend 
} from 'chart.js';
import ChartContainer from '@/Charts/ChartContainer.vue';

// 註冊所有需要的組件，包括 RadialLinearScale
ChartJS.register(
  RadarController,
  PointElement,
  RadialLinearScale, // 註冊 RadialLinearScale
  CategoryScale,
  Title,
  Tooltip,
  Legend
);

export default {
  name: 'InventorySC',
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
            backgroundColor: 'rgba(34,202,236,0.2)',
            borderColor: 'rgba(34,202,236,1)',
            pointBackgroundColor: 'rgba(34,202,236,1)',
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
        type: 'radar', // 確保使用的是 'radar' 類型
        data: this.chartData,
        options: { responsive: true, maintainAspectRatio: false }
      });
    }
  }
};
</script>

<style scoped>
canvas {
  width: 700px !important;
  height: 400px !important;
}
</style>
