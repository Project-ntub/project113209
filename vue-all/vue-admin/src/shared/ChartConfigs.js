export const chartConfigs = {
  RevenueChart: {
      name: 'RevenueChart',
      label: '營業額',
      chartType: 'bar',
      width: 300,
      height: 250,
      xAxisLabel: '店铺名稱',
      yAxisLabel: '營業額',
  },
  InventoryChart: {
      name: 'InventoryChart',
      label: '庫存量',
      chartType: 'bar',
      width: 300,
      height: 250,
      xAxisLabel: '商品名稱',
      yAxisLabel: '數量',
  },
  SalesChart: {
      name: 'SalesChart',
      label: '銷售額',
      chartType: 'line',
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

export function getChartConfig(chartName) {
return chartConfigs[chartName] || chartConfigs['SalesChart'];
}
