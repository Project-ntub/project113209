// src/shared/ChartConfigs.js
export const chartConfigs = {
    RevenueChart: {
      name: 'RevenueChart',
      label: '營業額',
      chartType: 'bar',  // 確認類型為 bar
      width: 300,
      height: 250,
      xAxisLabel: '店铺名稱',
      yAxisLabel: '營業額',
    },
    InventoryChart: {
      name: 'InventoryChart',
      label: '庫存量',
      chartType: 'bar',  // 確認類型為 bar
      width: 300,
      height: 250,
      xAxisLabel: '商品名稱',
      yAxisLabel: '數量',
    },
    SalesChart: {
      name: 'SalesChart',
      label: '銷售額',
      chartType: 'line',  // 確認類型為 line
      width: 300,
      height: 250,
      xAxisLabel: '日期',
      yAxisLabel: '銷售額',
    },
    ProductSalesPieChart: {
        name: 'ProductSalesPieChart',
        label: '產品銷售佔比',
        chartType: 'pie',
        width: 300,
        height: 250,
    },
};

// 獲取圖表配置的方法
export function getChartConfig(chartName) {
  return chartConfigs[chartName] || chartConfigs['SalesChart'];
}
