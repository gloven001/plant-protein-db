import streamlit as st
from supabase import create_client
import pandas as pd

# 1. 设置网页的整体风格 (宽屏模式看起来更大气)
st.set_page_config(page_title="植物蛋白数据库", page_icon="🌱", layout="wide")

# --- 隐藏右上角默认菜单和底部水印 (一点前端小魔法) ---
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("🌱 植物蛋白氨基酸图谱系统")
st.markdown("---") # 加一条优雅的分割线

# --- 安全连接数据库 ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("数据库连接异常，请检查后台 Secrets 配置。")
    st.stop()

# --- 搜索区域 (采用分栏让输入框不至于拉得太长) ---
col1, col2 = st.columns([2, 1])
with col1:
    search_term = st.text_input("🔍 输入原料名称进行精准查询 (例如：脱脂大豆粉)，留空显示全部")

try:
    # 去数据库查数据 (注意：请确保表名 'AA' 与你的 Supabase 完全一致)
    if search_term:
        response = supabase.table('Protein_AA').select("*").ilike('product_name', f'%{search_term}%').execute()
    else:
        response = supabase.table('Protein_AA').select("*").execute()
    
    if response.data:
        df = pd.DataFrame(response.data)
        
        # ==========================================
        # 🚀 核心颜值升级区域
        # ==========================================
        
        # 情况 A：如果只搜到 1 个具体产品，进入“高颜值详情模式”
        if len(df) == 1:
            st.success(f"🎯 成功锁定目标：**{df.iloc[0]['product_name']}**")
            
            # 提取该产品的各项氨基酸数据用来画图 (排除掉不需要画图的列)
            aa_data = df.drop(columns=['product_name', 'total', 'id', 'created_at'], errors='ignore').iloc[0]
            
            # 左右分栏：左边看核心数字，右边看图表
            c1, c2 = st.columns([1, 2])
            with c1:
                st.info("💡 核心营养指标")
                st.metric(label="总氨基酸含量", value=f"{df.iloc[0].get('total', 0)} mg/g")
                
                # 找出含量最高的那一项氨基酸
                max_aa_name = aa_data.idxmax()
                max_aa_value = aa_data.max()
                st.metric(label=f"最高含量氨基酸 ({max_aa_name.upper()})", value=f"{max_aa_value} mg/g")
            
            with c2:
                st.write("📊 **氨基酸组成图谱**")
                # 一行代码生成漂亮的动态柱状图
                st.bar_chart(aa_data) 
                
            st.write("📋 **详细数据对照表**")
            st.dataframe(df, use_container_width=True, hide_index=True)

        # 情况 B：如果展示的是多个产品的数据列表，进入“干净浏览模式”
        else:
            st.info(f"📂 当前展示 {len(response.data)} 种植物蛋白数据。输入具体名称可查看其专属图谱！")
            st.dataframe(
                df,
                use_container_width=True, 
                hide_index=True # 隐藏最左边难看的 0, 1, 2 序号
            )
            
    else:
        st.warning("数据库中暂时没有找到该原料，可能是拼写错误或暂未收录哦~")
        
except Exception as e:
    st.error(f"读取数据时发生错误：{e}")
