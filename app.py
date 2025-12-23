import gradio as gr
from datetime import datetime

# 物件データ保存
apartments = []
next_id = 1

def add_apartment(name, rent, station_min, floor, sunlight, noise, age, note):
    """物件追加"""
    
    if not name:
        # 入力エラー時は入力欄はそのまま（None を返して更新しない）
        return "物件名を入力してください", generate_table(), get_dropdown_update(), None, None, None, None, None, None, None, None
    
    global next_id
    apartment = {
        'id': next_id,
        'name': name,
        'rent': rent,
        'station_min': station_min,
        'floor': floor,
        'sunlight': sunlight,
        'noise': noise,
        'age': age,
        'note': note,
        'score': (sunlight + (10 - noise) + floor) / 3,  # 総合スコア
        'added': datetime.now().strftime('%m/%d %H:%M')
    }
    
    apartments.append(apartment)
    next_id += 1
    
    # 追加成功時は入力をデフォルトにリセット
    inputs_reset = get_inputs_reset()
    return f"✅ {name} を追加しました！", generate_table(), get_dropdown_update(), *inputs_reset

def generate_table():
    """比較表生成"""
    
    if not apartments:
        return "<p style='color:#999;text-align:center;padding:40px;'>まだ物件が登録されていません</p>"
    
    # スコア順にソート
    sorted_apts = sorted(apartments, key=lambda x: x['score'], reverse=True)
    
    html = """
    <style>
        .apt-table {width:100%; border-collapse:collapse; margin:20px 0;}
        .apt-table th {background:#667eea; color:white; padding:12px; text-align:left;}
        .apt-table td {padding:10px; border-bottom:1px solid #ddd;}
        .apt-table tr:hover {background:#f5f5f5;}
        .score {font-size:24px; font-weight:bold; color:#667eea;}
        .rank {background:#ffd700; color:#000; padding:3px 8px; border-radius:12px; font-weight:bold;}
        .rank-2 {background:#c0c0c0;}
        .rank-3 {background:#cd7f32;}
    </style>
    <table class='apt-table'>
        <tr>
            <th>順位</th>
            <th>物件名</th>
            <th>家賃</th>
            <th>駅徒歩</th>
            <th>階数</th>
            <th>日当たり</th>
            <th>静かさ</th>
            <th>築年数</th>
            <th>総合点</th>
            <th>登録日時</th>
        </tr>
    """
    
    for i, apt in enumerate(sorted_apts, 1):
        rank_class = 'rank' if i == 1 else f'rank-{i}' if i <= 3 else ''
        rank_badge = f"<span class='{rank_class}'>{i}位</span>" if i <= 3 else f"{i}位"
        
        html += f"""
        <tr>
            <td>{rank_badge}</td>
            <td><strong>{apt['name']}</strong><br><small style='color:#666;'>{apt['note']}</small></td>
            <td>¥{apt['rent']:,}</td>
            <td>{apt['station_min']}分</td>
            <td>{apt['floor']}階</td>
            <td>{'⭐' * apt['sunlight']}</td>
            <td>{'🔇' * (10 - apt['noise'])}</td>
            <td>{apt['age']}年</td>
            <td><span class='score'>{apt['score']:.1f}</span></td>
            <td><small>{apt['added']}</small></td>
        </tr>
        """
    
    html += "</table>"
    
    # 統計
    avg_rent = sum(a['rent'] for a in apartments) / len(apartments)
    html = f"""
    <div style='background:#e8f4f8;padding:20px;border-radius:8px;margin-bottom:20px;'>
        <h3>📊 物件統計</h3>
        <p>登録物件数: <strong>{len(apartments)}件</strong></p>
        <p>平均家賃: <strong>¥{avg_rent:,.0f}</strong></p>
        <p>最高評価: <strong>{sorted_apts[0]['name']}</strong> ({sorted_apts[0]['score']:.1f}点)</p>
    </div>
    """ + html
    
    return html

def get_dropdown_update():
    """ドロップダウンを更新"""
    choices = [f"{a['id']}: {a['name']}" for a in apartments]
    return gr.update(choices=choices, value=None)


def get_inputs_reset():
    """入力欄をデフォルト値（または空）にリセットする update を返す"""
    return (
        gr.update(value=""),        # name
        gr.update(value=80000),      # rent
        gr.update(value=5),          # station_min
        gr.update(value=3),          # floor
        gr.update(value=7),          # sunlight
        gr.update(value=3),          # noise
        gr.update(value=10),         # age
        gr.update(value=""),       # note
    )


def delete_apartment(selected):
    """選択した物件を削除"""
    if not selected:
        return "削除する物件を選択してください", generate_table(), get_dropdown_update()
    try:
        apt_id = int(selected.split(':', 1)[0])
    except:
        return "選択された項目が不正です", generate_table(), get_dropdown_update()
    for a in apartments:
        if a['id'] == apt_id:
            apartments.remove(a)
            return f"🗑️ {a['name']} を削除しました", generate_table(), get_dropdown_update()
    return "該当する物件が見つかりませんでした", generate_table(), get_dropdown_update()


def clear_all():
    """全削除"""
    global apartments, next_id
    apartments = []
    next_id = 1
    inputs_reset = get_inputs_reset()
    return "🗑️ 全ての物件を削除しました", generate_table(), get_dropdown_update(), *inputs_reset

# UI
with gr.Blocks(title="賃貸内見メモ", theme=gr.themes.Soft()) as demo:
    
    gr.Markdown("""
    # 🏠 賃貸内見メモ比較ツール
    ### 見た物件を記録して、ベストな部屋を見つけよう
    
    物件を見るたびに記録 → 自動で比較表作成 → 最適な物件が一目瞭然！
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📝 物件情報を入力")
            
            name = gr.Textbox(label="物件名", placeholder="例：グランメゾン新宿 301号室")
            
            with gr.Row():
                rent = gr.Number(label="家賃（円）", value=80000)
                station_min = gr.Number(label="駅徒歩（分）", value=5)
            
            with gr.Row():
                floor = gr.Slider(1, 20, value=3, step=1, label="階数")
                age = gr.Slider(0, 50, value=10, step=1, label="築年数")
            
            gr.Markdown("### ⭐ 主観評価（10段階）")
            
            sunlight = gr.Slider(1, 10, value=7, step=1, label="☀️ 日当たり")
            noise = gr.Slider(1, 10, value=3, step=1, label="🔊 騒音レベル（高いほどうるさい）")
            
            note = gr.Textbox(label="📌 メモ", placeholder="気になった点、良かった点など", lines=3)
            
            with gr.Row():
                add_btn = gr.Button("➕ 物件を追加", variant="primary", size="lg")
                clear_btn = gr.Button("🗑️ 全削除", variant="stop")
            
            gr.Markdown("### 🧹 誤登録を削除")
            delete_dropdown = gr.Dropdown(choices=[], label="削除する物件を選択")
            delete_btn = gr.Button("削除", variant="stop")
        
        with gr.Column(scale=2):
            status = gr.Markdown("物件を追加してください")
            comparison = gr.HTML()
    
    add_btn.click(
        fn=add_apartment,
        inputs=[name, rent, station_min, floor, sunlight, noise, age, note],
        outputs=[status, comparison, delete_dropdown, name, rent, station_min, floor, sunlight, noise, age, note]
    )
    
    clear_btn.click(
        fn=clear_all,
        outputs=[status, comparison, delete_dropdown, name, rent, station_min, floor, sunlight, noise, age, note]
    )
    
    delete_btn.click(
        fn=delete_apartment,
        inputs=[delete_dropdown],
        outputs=[status, comparison, delete_dropdown]
    )
    
    gr.Markdown("""
    ---
    ### 💡 使い方
    
    1. **内見したらすぐ記録**
       - 物件名、家賃、駅距離などを入力
       
    2. **主観評価を忘れずに**
       - 日当たり、騒音などの「感じ」を記録
       - 数字では分からない情報が大事！
       
    3. **メモを活用**
       - 「隣がコンビニで便利」
       - 「エレベーター古い」など
       
    4. **複数物件を比較**
       - 自動でランキング表示
       - 最高評価の物件が一目瞭然
    
    ---
    
    **Pro版（¥980）で追加予定：**
    - 📸 写真アップロード機能
    - 💾 データ保存・読み込み
    - 📊 詳細な分析グラフ
    - 📱 スマホアプリ対応
    """)

if __name__ == "__main__":
    demo.launch(share=True)