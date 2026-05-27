import pandas as pd
import os
import glob

# 投信欄位映射 (請確保與您 Excel 內的標題列名稱完全一致)
MAPPINGS = {
    "統一": {"code": "股票代號", "name": "股票名稱", "qty": "持股張數"},
    "00991A": {"code": "代碼", "name": "名稱", "qty": "持有張數"},
    "00992A": {"code": "代碼", "name": "名稱", "qty": "持有張數"}
}

def generate():
    os.makedirs('data/history', exist_ok=True)
    os.makedirs('dist', exist_ok=True)
    
    # 直接抓取所有 .xlsx 檔案
    all_files = glob.glob(os.path.join('data', "*.xlsx"))
    
    final_report = ""
    
    for file in all_files:
        key = os.path.basename(file).split('_')[0]
        mapping = MAPPINGS.get(key, MAPPINGS["統一"])
        
        # 1. 直接讀取 Excel 所有分頁並合併
        all_sheets = pd.read_excel(file, sheet_name=None)
        df_today = pd.concat(all_sheets.values(), ignore_index=True)
        
        # 2. 數據清洗 (移除逗號並轉數字)
        df_today[mapping['qty']] = df_today[mapping['qty']].astype(str).str.replace(',', '').astype(float)
        
        # 3. 比對邏輯
        history_path = f'data/history/{key}_last.xlsx'
        if os.path.exists(history_path):
            df_old = pd.read_excel(history_path)
            # 確保欄位名稱一致性
            merged = pd.merge(df_today, df_old, on=mapping['code'], how='outer', suffixes=('_now', '_old')).fillna(0)
            merged['diff'] = merged[f"{mapping['qty']}_now"] - merged[f"{mapping['qty']}_old"]
            
            # 只篩選有異動的
            changes = merged[merged['diff'] != 0]
            for _, row in changes.iterrows():
                css = "buy" if row['diff'] > 0 else "sell"
                final_report += f'<div class="item"><span>{row[mapping["code"]]} {row[mapping["name"]+"_now"]}</span><span class="{css}">{int(row["diff"])}</span></div>'
        
        # 4. 更新歷史檔
        df_today.to_excel(history_path, index=False)

    # 5. 生成 HTML
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        html = f.read().replace('<div id="content"></div>', final_report)
    with open('dist/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    generate()
