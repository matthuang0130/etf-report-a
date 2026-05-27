import pandas as pd
import os
import glob

MAPPINGS = {
    "統一": {"code": "股票代號", "name": "股票名稱", "qty": "持股張數"},
    "00991A": {"code": "代碼", "name": "名稱", "qty": "持有張數"},
    "00992A": {"code": "代碼", "name": "名稱", "qty": "持有張數"}
}

def load_file(file_path, mapping):
    # 自動偵測格式
    if file_path.endswith('.xlsx'):
        all_sheets = pd.read_excel(file_path, sheet_name=None)
        df = pd.concat(all_sheets.values(), ignore_index=True)
    else:
        df = pd.read_csv(file_path)
    
    # 清洗數據
    df[mapping['qty']] = df[mapping['qty']].astype(str).str.replace(',', '').astype(float)
    return df

def generate():
    os.makedirs('data/history', exist_ok=True)
    
    # 同時搜尋 xlsx 和 csv
    all_files = glob.glob(os.path.join('data', "*.*"))
    
    final_report = ""
    for file in all_files:
        if not (file.endswith('.xlsx') or file.endswith('.csv')): continue
            
        key = os.path.basename(file).split('_')[0]
        mapping = MAPPINGS.get(key, MAPPINGS["統一"])
        
        df_today = load_file(file, mapping)
        
        # 比對邏輯
        history_path = f'data/history/{key}_last.csv'
        if os.path.exists(history_path):
            df_old = pd.read_csv(history_path)
            merged = pd.merge(df_today, df_old, on=mapping['code'], how='outer', suffixes=('_now', '_old')).fillna(0)
            merged['diff'] = merged[f"{mapping['qty']}_now"] - merged[f"{mapping['qty']}_old"]
            
            changes = merged[merged['diff'] != 0]
            for _, row in changes.iterrows():
                css = "buy" if row['diff'] > 0 else "sell"
                final_report += f'<div class="item"><span>{row[mapping["code"]]} {row[mapping["name"]+"_now"]}</span><span class="{css}">{int(row["diff"])}</span></div>'
        
        # 存入歷史檔 (統一存為 csv，方便讀取)
        df_today.to_csv(history_path, index=False)

    # 生成 HTML (保持不變)
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        html = f.read().replace('<div id="content"></div>', final_report)
    with open('dist/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    generate()
