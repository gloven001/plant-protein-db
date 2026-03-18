import streamlit as st
from supabase import create_client
import pandas as pd

# 设置网页标签页的标题和图标
st.set_page_config(page_title="植物蛋白数据库", page_icon="🌱", layout="wide")

st.title("🌱 植物蛋白氨基酸查询系统")
st.write("欢迎使用！你可以搜索特定原料，或者直接查看全部数据。")

# --- 安全连接数据库 ---
# 注意：这里千万不要直接写死你的密码！我们将通过 Streamlit 的安全后台来读取
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("数据库配置未完成，请在后台设置 Secrets。")
    st.stop()

# --- 搜索与展示区域 ---
search_term = st.text_input("🔍 搜索产品名称 (例如：大豆、豌豆)，留空则显示全部数据")

try:
    # 根据搜索框的内容去数据库查数据
    if search_term:
        # ilike 表示模糊搜索，只要名字里包含你输入的字就能搜出来
        response = supabase.table('plant_proteins').select("*").ilike('product_name', f'%{search_term}%').execute()
    else:
        # 如果什么都没输入，就展示所有数据
        response = supabase.table('plant_proteins').select("*").execute()
    
    # 将查到的数据展示出来
    if response.data:
        st.success(f"共找到 {len(response.data)} 条数据！")
        # 将数据转换为 Pandas 表格格式，在网页上展示会更美观、可排序
        df = pd.DataFrame(response.data)
        st.dataframe(df, use_container_width=True)
    else:
        st.warning("数据库中暂时没有找到匹配的原料哦~")
        
except Exception as e:
    st.error(f"读取数据时发生错误：{e}")
