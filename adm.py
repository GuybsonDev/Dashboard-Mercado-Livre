import streamlit as st

st.set_page_config(page_title='DashML', page_icon='content/logo.png', layout='wide')

pages = [
    st.Page("paginas/produtos.py", title='Início'),
]

with st.sidebar:
    st.image('content/logo.png')

pg = st.navigation({"Navegação": pages}, position='sidebar')
pg.run()