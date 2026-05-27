import pandas as pd
import os
import glob

# 1. 欄位設定
MAPPINGS = {
    "統一": {"code": "股票代號", "name": "股票名稱", "qty": "持股張數"},
    "00991A": {"code": "代碼", "name": "名稱", "qty": "持有張數"},
    "00992A": {"code": "代碼", "name": "名稱", "qty": "持有張數"}
}

def generate():
    # 建立目錄
    os.makedirs('data/history', exist_ok=True)
    os.makedirs('dist', exist_ok=True)
    
    # 讀取所有目前的檔案
    all_files = glob.glob(os.path.join('data', "*.csv"))
    
    # 依據檔名開頭 (如 00992A) 分組
    groups = {}
    for f in all_files:
        key = os.path.basename(f).split('_')[0]
        if key not in groups: groups[key] = []
        groups[key].append(f)
    
    final_report = ""
    
    for key, files in groups.items():
        mapping = MAPPINGS.get(key, MAPPINGS["統一"])
        
        # 讀取並合併該組所有 CSV (例如群益的三個頁面)
        df_list = [pd.read_csv(f) for f in files]
        df_today = pd.concat(df_list)
        df_today[mapping['qty']] = df_today[mapping['qty']].astype(str).str.replace(',', '').astype(float)
        
        # 比對邏輯：檢查歷史檔
        history_path = f'data/history/{key}_last.csv'
        if os.path.exists(history_path):
            df_old = pd.read_csv(history_path)
            merged = pd.merge(df_today, df_old, on=mapping['code'], how='outer', suffixes=('_now', '_old')).fillna(0)
            merged['diff'] = merged[f"{mapping['qty']}_now"] - merged[f"{mapping['qty']}_old"]
            
            # 只篩選有異動的
            changes = merged[merged['diff'] != 0]
            for _, row in changes.iterrows():
                css = "buy" if row['diff'] > 0 else "sell"
                final_report += f'<div class="item"><span>{row[mapping["code"]]} {row[mapping["name"]+"_now"]}</span><span class="{css}">{int(row["diff"])}</span></div>'
        
        # 更新歷史檔
        df_today.to_csv(history_path, index=False)

    # 寫入 HTML (這裡會自動更新 dist/index.html)
    with open('templates/index.html', 'r', encoding='utf-8') as f:
        html = f.read().replace('<div id="content"></div>', final_report)
    with open('dist/index.html', 'w', encoding='utf-8') as f:
        f.write(html)

generate()
