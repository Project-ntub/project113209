# generate_chart.py
import os
import sys

# 將專案目錄附加到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'project113209'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project113209.settings')
import django
django.setup()

import requests
import plotly.graph_objects as go

# 使用你獲取的JWT access token
headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzI1NTQxMzIzLCJpYXQiOjE3MjU0NTQ5MjMsImp0aSI6IjY3MjFmMmZjNjc3OTQ5NmFhYjU4Y2YyMTBmMTZmODJiIiwidXNlcl9pZCI6MzZ9.ytJu1b5FwJXUJ7ZpkyX2H8sXou8d96roHMHCmPOw8Bk'}

# 從後端API獲取數據
response = requests.get('http://127.0.0.1:8000/api/backend/sales-chart-data/', headers=headers)
data = response.json()

# 確認API返回的數據是否包含必要的字段
if 'data' in data and 'layout' in data:
    plot_data = data['data']
    plot_layout = data['layout']

    # 使用Plotly顯示圖表
    fig = go.Figure(data=plot_data)
    fig.update_layout(plot_layout)
    fig.show()
else:
    print("API返回的數據格式不正確或不完整")