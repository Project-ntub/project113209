# generate_chart.py
import plotly.graph_objs as go
import plotly.io as pio

# 創建一個簡單的柱狀圖
fig = go.Figure(data=[go.Bar(x=[1, 2, 3], y=[3, 1, 6])])
# 將圖表轉換為 HTML
html_str = pio.to_html(fig, full_html=False)

# 將 HTML 保存到文件中
with open("chart.html", "w") as f:
    f.write(html_str)
