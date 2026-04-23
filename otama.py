import streamlit as st
from supabase import create_client
from datetime import datetime

# Supabase接続
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ページ選択
page = st.sidebar.selectbox("ページを選択", ["名前登録", "じゃんけん記録"])

# ==================
# 名前登録ページ
# ==================
if page == "名前登録":
    st.title("名前登録")
    
    name = st.text_input("ニックネームを入力")
    
    if st.button("登録"):
        if not name:
            st.warning("名前を入力してください")
        else:
            supabase.table("profiles").insert({"name": name}).execute()
            st.success(f"「{name}」を登録しました！")

# ==================
# じゃんけん記録ページ
# ==================
elif page == "じゃんけん記録":
    st.title("じゃんけん記録")

    # プレイヤー数選択
    num_players = st.selectbox("プレイヤー数を選択", [2, 3, 4])

    # profilesから名前を取得
    players = supabase.table("profiles").select("name").execute()
    player_names = [p["name"] for p in players.data]

    if not player_names:
        st.warning("先に名前を登録してください")
    else:
        # ラウンド数入力
        round_number = st.number_input("ラウンド数", min_value=1, value=1)

        st.subheader("各プレイヤーの手を入力")

        moves_input = []
        for i in range(num_players):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                name = st.selectbox(f"プレイヤー{i+1}", player_names, key=f"name_{i}")
            with col2:
                move = st.selectbox("手", ["グー", "チョキ", "パー"], key=f"move_{i}")
            with col3:
                loser = st.checkbox("負け", key=f"loser_{i}")
            with col4:
                money = st.number_input("負け金額", min_value=0, value=0, key=f"money_{i}")
            moves_input.append({"name": name, "move": move, "loser": loser, "money": money})

        if st.button("保存"):
            # セッション保存
            session = supabase.table("janken_sessions").insert({
                "round_number": round_number,
                "played_at": datetime.now().isoformat()
            }).execute()

            session_id = session.data[0]["session_id"]

            # 各プレイヤーの手を保存
            for m in moves_input:
                supabase.table("janken_moves").insert({
                    "session_id": session_id,
                    "player_name": m["name"],
                    "move": m["move"],
                    "loser": m["loser"],
                    "money": m["money"]
                }).execute()

            st.success("保存完了！")
            st.balloons()
