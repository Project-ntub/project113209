import axios from 'axios';

export const fetchChartData = async (chartConfig) => {
  if (!chartConfig.dataSource || !chartConfig.xAxisField) {
    console.error('資料來源和 X 軸欄位必須設置');
    return null;
  }

  try {
    const requestData = {
      table_name: chartConfig.dataSource,
      x_field: chartConfig.xAxisField,
      filter_conditions: chartConfig.filterConditions || {},
      chart_type: chartConfig.chartType,
      y_field: chartConfig.yAxisField,
      y_fields: chartConfig.yAxisFields?.filter(field => field) || [], // 過濾掉 null 或未定義的值
      ordering: chartConfig.ordering || [],
      limit: chartConfig.limit || null,
    };

    const response = await axios.post('/api/backend/dynamic-chart-data/', requestData);
    const responseData = response.data;

    if (chartConfig.chartType === 'combo') {
      return {
        x_data: responseData.x_data,
        y_data_bar: responseData.y_data_bar,
        y_data_line: responseData.y_data_line,
        y_field_bar: responseData.y_field_bar,
        y_field_line: responseData.y_field_line,
      };
    } else {
      return {
        x_data: responseData.x_data,
        y_data: responseData.y_data,
      };
    }
  } catch (error) {
    console.error('獲取圖表數據時出錯:', error);
    throw error;
  }
};
