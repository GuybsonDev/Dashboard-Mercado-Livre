import requests
import pandas as pd
import streamlit as st
import altair as alt
import plotly.express as px
import json

# Função para consumir a API do Mercado Livre e trazer produtos e informações
def buscar_produto_mercadolivre(nome_produto):
    url = f"https://api.mercadolibre.com/sites/MLB/search?q={nome_produto}"
    response = requests.get(url)
    
    if response.status_code == 200:
        dados = response.json()
        dados_formatados = json.dumps(dados["results"], indent=4, ensure_ascii=False)
        
        produtos = dados.get("results", [])
        if len(produtos) != 0:
        
            produtos_encontrados = []
            
            for produto in produtos:
                produtos_encontrados.append({
                    "Nome": produto["title"],
                    "Preço": produto["price"],
                    "Preço Original": produto["original_price"],
                    "Imagem": produto["thumbnail"],
                    "Quantidade Disponível": produto.get("available_quantity", 0),
                    "Link": produto["permalink"],
                    "Vendedor": produto["seller"]["nickname"]
                })
            
            return produtos_encontrados
        else:
            return produtos
        
    else:
        st.error(f"Erro ao acessar a API: {response.status_code}")
        return []

# Sidebar para entrada do nome do produto
with st.sidebar:
    produto = st.text_input('Informe o produto')
    
# Se o usuário fornecer o nome do produto, busca e exibe os dados
if produto:
    
    # Requisitando a API do mercado livre. Variável "resultados" trás todas informações do produto
    resultados = buscar_produto_mercadolivre(produto)
    
    if len(resultados) == 0:
        # Setando o titulo da página
        st.subheader(f'Não há nenhum resultado para essa pesquisa', divider='rainbow')
    
    else:

        # Setando o titulo da página
        st.subheader(f'Visualização de dados relacionados a {produto}', divider='rainbow')
        
        # Criando o dataframe com essas informações e filtrando por preço de forma decrescente
        df_geral = pd.DataFrame(resultados).sort_values(by='Preço', ascending=False)
        
        # Criando dataframe com coluna onde terá o valor do desconto ao invés da porcentagem
        df_valor_desconto = df_geral.copy()
        df_valor_desconto['Preço Original'] = df_valor_desconto['Preço Original'] - df_valor_desconto['Preço']
        
        #Calculando a média de valor antes de acrescentar o R$
        media_produtos = df_geral["Preço"].mean()
        media_produtos = round(media_produtos, 2)

        # Calculando a porcentagem de desconto
        df_geral["Desconto %"] = ((df_geral["Preço Original"] - df_geral["Preço"]) / df_geral["Preço Original"]) *100
        
        
        # Substituindo NaN da coluna "Porcentagem %" por 0 e tornando a coluna em inteiro
        df_geral["Desconto %"] = df_geral["Desconto %"].fillna(0).astype(int)
        
        # Formatando a coluna "Preço" para exibir em reais e formato para segunda casa decimal
        df_geral['Preço'] = df_geral['Preço'].apply(lambda x: f'R$ {x:,.2f}')
        
        # Gerando as colunas
        col1, col2= st.columns([7,1.2])
        
        
        with col2:
            # Criando container que preencherá toda col2
            with st.container(border=True, height=850):
                st.subheader('_Valores_',divider='rainbow')
                with st.container(border=True):
                    st.markdown('Média de valor do produto:')
                    st.markdown(f' R$ {media_produtos}')
                    
                with st.container(border=True):
                    # Exibindo a imagem do produto mais caro
                    st.markdown('_Produto de maior valor_')
                    st.markdown(df_geral.iloc[0]["Preço"])
                    st.image(df_geral.iloc[0]["Imagem"], width=220)
                    
                with st.container(border=True):
                    # Exibindo a imagem do produto mais barato
                    st.markdown('_Produto de menor valor_')
                    st.markdown(df_geral.iloc[-1]["Preço"])
                    st.image(df_geral.iloc[-1]["Imagem"], width=200)
        
        # Definir a coluna "Imagem" como índice
        df_geral.set_index("Imagem", inplace=True)
        
        # Contando quantas vezes cada vendedor aparece
        contagem_vendedores = df_geral['Vendedor'].value_counts().reset_index()
        
        # Adicionando uma coluna com a porcentagem
        contagem_vendedores['percentual'] = (contagem_vendedores['count'] / contagem_vendedores['count'].sum()) * 100

        # Formatando a coluna percentual com duas casas decimais
        contagem_vendedores['percentual'] = contagem_vendedores['percentual'].round(2)
        
        # Retirnado a quantidaade de produtos apresentados, quantidade de vendedores e trazendo a media de quantos produtos daquele modelo cada vendedor vende.
        quantidade_de_produtos = contagem_vendedores['count'].sum()
        quantidade_de_vendedores = contagem_vendedores['Vendedor'].count()
        media_de_produtos_por_vendedor = quantidade_de_produtos / quantidade_de_vendedores
        
        # Encontrando o vendedor que mais vendeu (aquele com o maior valor de 'count')
        vendedor_mais_vendido = contagem_vendedores.loc[contagem_vendedores['count'].idxmax(), 'Vendedor']
        # Obtendo a quantidade de produtos vendidos pelo vendedor mais vendido
        quantidade_vendas_vendedor_mais_vendido = contagem_vendedores.loc[contagem_vendedores['Vendedor'] == vendedor_mais_vendido, 'count'].values[0]
        # Calculando o percentual acima da média
        percentual_acima_da_media = ((quantidade_vendas_vendedor_mais_vendido - media_de_produtos_por_vendedor) / media_de_produtos_por_vendedor) * 100
        percentual_acima_da_media = int(percentual_acima_da_media)
        # Encontrando o vendedor que menos vendeu (aquele com o menor valor de 'count')
        vendedor_menos_vendido = contagem_vendedores.loc[contagem_vendedores['count'].idxmin(), 'Vendedor']
        # Obtendo a quantidade de produtos vendidos pelo vendedor menos vendido
        quantidade_vendas_vendedor_menos_vendido = contagem_vendedores.loc[contagem_vendedores['Vendedor'] == vendedor_menos_vendido, 'count'].values[0]
        # Calculando o percentual acima da média
        percentual_abaixo_da_media = ((quantidade_vendas_vendedor_menos_vendido - media_de_produtos_por_vendedor) / media_de_produtos_por_vendedor) * 100
        percentual_abaixo_da_media = int(percentual_abaixo_da_media)
        # Trazendo o produto com maior Quantidade disponível
        quantidade_maxima = df_geral['Quantidade Disponível'].max()
        quantidade_maxima = int(quantidade_maxima)
        
        # Criando o dataframe visual para não ser utilizado o original
        df_visual = df_geral.copy()
        df_visual = df_geral.drop(columns='Preço Original')
        
        # Ajustando colunas do dataframe para visualização
        df_visual = df_visual.reindex(columns=['Nome', 'Vendedor', 'Preço', 'Desconto %', 'Quantidade Disponível', 'Link'])
        
        with col1:
            with st.container(border=True):
                # Configurando a coluna de imagem com st.column_config.ImageColumn e gráfico
                st.dataframe(
                    df_visual,
                    column_config={
                        "Imagem": st.column_config.ImageColumn("Imagem"),
                        "Link": st.column_config.LinkColumn('Link'),
                        "Quantidade Disponível": st.column_config.ProgressColumn("Quantidade Disponível", format='%d', max_value=quantidade_maxima),
                        "Desconto %": st.column_config.ProgressColumn('Desconto %')
                    }, use_container_width=True, height=810
                )
                
        # Criando o gráfico com o eixo X invertido para o centro superior
        chart = alt.Chart(contagem_vendedores).mark_bar(color='#FF4B4B', size=10).encode(
            y=alt.Y(
                'Vendedor', 
                title='Vendedor', 
                sort='-x',  # Ordena os vendedores do maior para o menor com base no eixo X
                axis=alt.Axis(labelFontSize=15, labelPadding=30)
            ),  # Eixo vertical
            x=alt.X(
                'count', 
                title='Quantidade', 
                axis=alt.Axis(orient='top', format='d')
            )  # Eixo horizontal no topo
        ).properties(
            width=400,
            height=800,
        )

        # Criando as colunas que ficam abaixo do dataframe
        col10, col20, col30 = st.columns([3.5,3.5, 1.2])
        
        with col10:
            with st.container(border=True, height=700):
                # Visualizando o gráfico no streamlit
                st.markdown('Quantidade de modelos do produto por vendedor')
                st.altair_chart(chart, use_container_width=True)
                
        # Retirando os NaN do dataframe df_valor_desconto['Preço Original']
        df_valor_desconto = df_valor_desconto.dropna(subset=['Preço Original'])      
        
        # Criando o gráfico com o eixo X invertido para o centro superior
        chart1 = alt.Chart(df_valor_desconto).mark_bar(color='#FF4B4B', size=10).encode(
            y=alt.Y(
                'Vendedor', 
                title='Vendedor', 
                sort='-x',  # Ordena os vendedores do maior para o menor com base no eixo X
                axis=alt.Axis(labelFontSize=15, labelPadding=30)
            ),  # Eixo vertical
            x=alt.X(
                'Preço Original', 
                title='Desconto', 
                axis=alt.Axis(orient='top',format="$,.2f")
            )  # Eixo horizontal no topo
        ).properties(
            width=400,
            height=800,
        )
        
        # Inicializando a coluna col20
        with col20:
            with st.container(border=True, height=700):
                st.markdown('Desconto por Vendedor')
                st.altair_chart(chart1, use_container_width=True)
                        
        # Criando o gráfico de pizza
        fig = px.pie(
            contagem_vendedores,
            values='percentual',
            names='Vendedor',
            title='Distribuição de Vendedores (%)',
        )

        # Atualizando o tooltip para mostrar a porcentagem após o valor
        fig.update_traces(
            hovertemplate="<b>%{label}</b><br>Quantidade: %{value}<br>Porcentagem: %{percent:.1%}",  # Customiza o tooltip
            textinfo='none',  # Remove o texto diretamente nas fatias
        )

        # Removendo a legenda
        fig.update_layout(
            showlegend=False,  # Oculta a legenda
            width=500,  # Definindo a largura
            height=350,  # Definindo a altura
        )
        
        with col30: 
            with st.container(border=True, height=700):
                st.subheader('_Produtos/Vendedores_', divider='rainbow')
                with st.container(border=True):
                    st.markdown(f'Quantidade de produtos apresentados: {quantidade_de_produtos}')
                with st.container(border=True):
                    st.markdown('Vendedor mais exibido:')
                    st.metric(vendedor_mais_vendido, f'{quantidade_vendas_vendedor_mais_vendido} Produtos', f'{percentual_acima_da_media}%')
                # Exibindo o gráfico no Streamlit
                st.plotly_chart(fig, use_container_width=True)
                print(df_valor_desconto['Preço Original'])

else:
    st.subheader('_Informe um produto para apresentação dos dados._')
    

