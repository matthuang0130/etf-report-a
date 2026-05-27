import pandas as pd
import os
import glob

# 設定路徑
data_folder = 'data'
template_path = 'templates/index.html'
output_folder = 'dist'
if not os.path.exists(output_folder): os.makedirs(output_folder)

def get_html_item(row):
    # 處理名稱和標籤
    name = str(row['證券名稱'])
    change = float(row['張數變動(張)'])
    status = str(row['變動狀態'])
    
    css_class = "buy" if change > 0 else "sell"
    change_text = f"+{int(change)}" if change > 0 else f"{int(change)}"
    
    tag = ""
    if "新" in status: tag = '<span class="tag">新</span>'
    elif "出清" in status: tag = '<span class="tag">出清</span>'
    
    return f'<div class="item"><span>{row["證券代號"]} {name}{tag}</span><span class="{css_class}">{change_text}</span></div>'

# 讀取模板
with open(template_path, 'r', encoding='utf-8') as f:
    template = f.read()

# 解析 Excel (假設 data 資料夾內有對應檔案)
all_html = ""
for file in glob.glob(os.path.join(data_folder, "*.xlsx")):
    df = pd.read_excel(file)
    etf_name = os.path.basename(file).split('_')[1]
    
    items = "".join([get_html_item(row) for _, row in df.iterrows()])
    all_html += f'<div class="title">{etf_name}</div><div class="grid"><div class="box">{items}</div></div>'

# 生成最終頁面
final_html = template.replace('<div id="content"></div>', all_html)
with open(os.path.join(output_folder, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(final_html)

print("自動轉換完成！")
