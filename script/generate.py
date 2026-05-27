import pandas as pd
import os

# 自動讀取 data 資料夾內的所有 Excel
data_folder = 'data'
output_folder = 'dist'
if not os.path.exists(output_folder): os.makedirs(output_folder)

# 之後我們會在這裡寫入處理邏輯，把 Excel 轉換為 HTML
print("自動轉換程序啟動中...")
