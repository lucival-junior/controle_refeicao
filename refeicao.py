#importe dos pacotes
import streamlit as st
import pandas as pd
from PIL import Image
import  time
import base64
import plotly.graph_objs as go
import numpy as np

#carrega logo do empresa
image = Image.open('logo-grupo-sococo.png')
st.image(image,width=700 , caption='Cálculo de Refeições Extras')

#variaveis de arquivo saida
primeira_limpeza = "primeira_limpeza.txt"
segunda_limpeza = "segunda_limpeza.txt"

#busca para limpeza
search_for = '21'
search_for2 = "SOCOCO"

st.set_option('deprecation.showfileUploaderEncoding', False)
#recebe o arquivo de texto do usuário
uploaded_file = st.file_uploader("Selecione ou arraste seu arquivo gerado pelo TSA: ",
                                 type="txt", encoding="windows-1252")
#formata o arquivo recebido em 06 colunas
colunas = [5,11,28,12,7,7]

if uploaded_file is not None:
# se o arquivo foi carregado, le o arquivo e gera um novo arquivo formatado
    data = pd.read_fwf(uploaded_file, widths=colunas, header=None)
    data.to_csv('arquivo_sem_tratamento.txt', index=False)
    # st.write(data)

# Inicia a primeira limpeza do arquivo gerado acima.
# Gera um novo aquivo com a primeira limpeza concluida.
    with open(primeira_limpeza, 'w', encoding="windows-1252") as out_f:
        with open('arquivo_sem_tratamento.txt', "r") as in_f:
            for line in in_f:
                if search_for in line:
                    out_f.write(line)

# Inicia a segunda limpeza do arquivo gerado acima.
# Gera o arquivo final limpo
    with open(segunda_limpeza, 'w', encoding="windows-1252") as out_f:
        with open('primeira_limpeza.txt', "r", encoding="windows-1252") as in_f:
            for line in in_f:
                if search_for2 in line:
                    pass
                else:
                  out_f.write(line)

#carrega arquivo da segunda limpeza e gera o arquivo final limpo para mostrar na tela
    df = pd.read_csv('segunda_limpeza.txt', sep=',')
    df.columns = ['Empresa', 'Matricula', 'Funcionario', 'Data', 'Hora', 'Refeicao']
    df.to_csv('arquivo_limpo.txt', index=False)

    with st.spinner('Aguarde o carregamento do arquivo...'):
        time.sleep(5)
    #st.success('Concluido!')
    #st.write(df)
    #st.write("Linha / Colunas: ", df.shape)


    if st.checkbox('Desconto por Funcionário'):
        #hora_inicial = st.sidebar.text_input('Hora inicial', '06:00')
        #hora_final = st.sidebar.text_input('Hora final', '08:00')

        #filtro_hora = df.loc[(df['Hora'] >= hora_inicial) & (df['Hora']<= hora_final)]
        #st.write(filtro_hora)
        #st.write("Linha / Colunas: ",filtro_hora.shape)

        #inicio de novo tratamento e criacao de novas colunas

        #trasnformar categoria REFEICAO para fator (ALMOÇO - 0/1	CAFE- 0/1	CEIA- 0/1	JANTAR- 0/1	LANCHE- 0/1)
        filtro_ref = pd.get_dummies(df['Refeicao'])
        #concatena df inicial com novas colunas geradas pelo fator
        novo_df = pd.concat([df, filtro_ref], axis=1, sort=False)

        #remove as colunas (Empresa , Hora , Refeicao) para melhor visualizacao
        novo_df2 = novo_df.drop(columns=['Empresa','Hora','Refeicao'])

        # criar indice para agrupar refeicoes por dia
        # 'estilo' contador para adiconar preco diferente
        mat_dia = novo_df2.groupby(['Matricula','Funcionario','Data']).sum()

        #adiciona novas colunas para visualização
        # mat_dia['VALOR_FUN'] = 0
        # mat_dia['VALOR_INT'] = 0


#----------------------------------------------------------#
        #Funcao para calculo das refeicoes
        def lanche(lan):
            if (lan['LANCHE'] == 1) & (lan['CAFE'] == 0):
                return lan['LANCHE'] * 0 and lan['CAFE'] * 0
            elif lan['LANCHE'] == 1 & lan['CAFE'] == 1:
                return lan['LANCHE'] * 0 and lan['CAFE'] * 3.41
            elif (lan['LANCHE'] > 1) & (lan['CAFE'] == 0):
                return lan['LANCHE'] * 3.41 - 3.41
            elif (lan['LANCHE'] > 1) & (lan['CAFE'] >= 1):
                return lan['LANCHE'] * 3.41
            else:
                return 0
        calculo_lanche = mat_dia.apply(lanche, axis=1)

        def cafe(caf):
            if (caf['LANCHE'] == 1) & (caf['CAFE'] == 0):
                return caf['CAFE'] * 0
            elif caf['LANCHE'] == 1 & caf['CAFE'] == 1:
                return caf['CAFE'] * 3.41
            elif (caf['LANCHE'] == 0) & (caf['CAFE'] > 1):
                return caf['CAFE'] * 3.41 - 3.41
            elif (caf['LANCHE'] >= 1) & (caf['CAFE'] > 1):
                return caf['CAFE'] * 3.41
            else:
                return 0
        calculo_cafe = mat_dia.apply(cafe, axis=1)


        # lista de condicoes para desconto
        conditions = [
            (mat_dia['ALMOÇO'] == 1) & (mat_dia['CEIA'] == 0) & (mat_dia['JANTAR'] == 0),
            (mat_dia['ALMOÇO'] == 1) & (mat_dia['CEIA'] == 1) & (mat_dia['JANTAR'] == 1),
            (mat_dia['ALMOÇO'] == 1) & (mat_dia['CEIA'] == 1) & (mat_dia['JANTAR'] == 0),
            (mat_dia['ALMOÇO'] == 1) & (mat_dia['CEIA'] == 0) & (mat_dia['JANTAR'] == 1),
            (mat_dia['ALMOÇO'] > 1) & (mat_dia['CEIA'] == 0) & (mat_dia['JANTAR'] == 0),
            (mat_dia['ALMOÇO'] > 1) & (mat_dia['CEIA'] != 0) | (mat_dia['JANTAR'] != 0),
            (mat_dia['ALMOÇO'] == 0) & (mat_dia['CEIA'] != 0) | (mat_dia['JANTAR'] != 0)]
        # escolhas de acordo com a lista de desconto ocorrida
        choices = [0.0,
                   (mat_dia['ALMOÇO'] * 8.85 + mat_dia['CEIA'] * 8.85 + mat_dia['JANTAR'] * 8.85) - 8.85,
                   (mat_dia['ALMOÇO'] * 8.85 + mat_dia['CEIA'] * 8.85 + mat_dia['JANTAR'] * 8.85) - 8.85,
                   (mat_dia['ALMOÇO'] * 8.85 + mat_dia['CEIA'] * 8.85 + mat_dia['JANTAR'] * 8.85) - 8.85,
                   (mat_dia['ALMOÇO'] * 8.85) - 8.85,
                   (mat_dia['ALMOÇO'] * 8.85 + mat_dia['CEIA'] * 8.85 + mat_dia['JANTAR'] * 8.85) - 8.85,
                   (mat_dia['ALMOÇO'] * 0 + mat_dia['CEIA'] * 8.85 + mat_dia['JANTAR'] * 8.85) - 8.85]

        #soma de valores na coluna DESCONTAR
        mat_dia['NUM_REFEICOES'] = mat_dia['ALMOÇO'] + mat_dia['CAFE']+ mat_dia['CEIA']+ \
                               mat_dia['JANTAR']+ mat_dia['LANCHE']

        mat_dia['DESCONTO_1'] = calculo_cafe + calculo_lanche
        mat_dia['DESCONTO_2'] = np.select(conditions, choices, default=0.0)
        st.markdown('Refeições por funcionário')
        st.write(mat_dia)
        st.write("Linha / Colunas: ", mat_dia.shape)

        # Filtro para saber quem teve refeicoes em excesso.
        filtrado = mat_dia.loc[(mat_dia['NUM_REFEICOES'] >= 3) | (mat_dia['ALMOÇO']==2) |(mat_dia['CAFE']==2) |
                               (mat_dia['CEIA']==2) |  (mat_dia['JANTAR']==2) | (mat_dia['LANCHE']==2) ]

        filtrado['DESCONTO_TOTAL'] = mat_dia['DESCONTO_1'] + mat_dia['DESCONTO_2']
        filtrado.DESCONTO_2 = filtrado.DESCONTO_2.round(2)
        filtrado.DESCONTO_TOTAL = filtrado.DESCONTO_TOTAL.round(2)

        st.markdown('Refeições EXTRA por funcionário')
        st.write(filtrado)
        st.write("Linha / Colunas: ", filtrado.shape)

        #salva o arquivo em formato de texto com os INDÍCES para download
        filtrado.to_csv('refeicoes_extras.txt')

        #funcao para gerar downlod da data frame tratado
        def download_link(object_to_download, download_filename, download_link_text):

            if isinstance(object_to_download, pd.DataFrame):
                object_to_download = object_to_download.to_csv(index=True)
                b64 = base64.b64encode(object_to_download.encode()).decode()
                return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

        if st.button('Download'):
            tmp_download_link = download_link(filtrado, 'refeicoes_extras.txt', 'Clique para salvar o arquivo')
            st.markdown(tmp_download_link, unsafe_allow_html=True)

#----------------------------------------------------------#
        #Gráfico numero de refeicoes
    if st.checkbox('Quantidade de Refeições'):
        quantidade_cafe = sum((df['Refeicao']=='CAFE') )
        quantidade_almoco = sum((df['Refeicao']=='ALMOÇO') )
        quantidade_lanche = sum((df['Refeicao']=='LANCHE') )
        quantidade_janta = sum((df['Refeicao']=='JANTAR') )
        quantidade_ceia = sum((df['Refeicao']=='CEIA') )

        lista_grafico = [quantidade_cafe, quantidade_almoco,
                        quantidade_lanche, quantidade_janta,
                        quantidade_ceia]

        #verificar para melhorar esse codigo
        total_ref_periodo = (quantidade_cafe + quantidade_almoco +
                            quantidade_lanche + quantidade_janta +
                             quantidade_ceia)

        # configure_plotly_browser_state()
        trace = go.Bar(x=['Café', 'Almoço', 'Lanche', 'Janta','Ceia'],
                       y=lista_grafico)

        legenda = go.Layout(title='Quantidade de refeições por tipo',
                            xaxis={'title': 'Tipo de Refeição'},
                            yaxis={'title': 'Quantidade'}
                            )
        figura = go.Figure(data=trace, layout=legenda)
        st.write(figura)

#-------------------------------------------------------------------------#
        #Gráfico de reficoes extras
        if st.checkbox('Quantidade EXTRA de Refeições'):
            quantidade_cafe_filtrado = sum(filtrado['CAFE'])
            quantidade_almoco_filtrado = sum(filtrado['ALMOÇO'])
            quantidade_lanche_filtrado = sum(filtrado['LANCHE'])
            quantidade_janta_filtrado = sum(filtrado['JANTAR'])
            quantidade_ceia_filtrado = sum(filtrado['CEIA'])

            lista_grafico_filtrado = [quantidade_cafe_filtrado, quantidade_almoco_filtrado,
                             quantidade_lanche_filtrado, quantidade_janta_filtrado,
                             quantidade_ceia_filtrado]

            # verificar para melhorar esse codigo
            total_ref_periodo_filtrado = (quantidade_cafe_filtrado + quantidade_almoco_filtrado +
                                 quantidade_lanche_filtrado + quantidade_janta_filtrado +
                                 quantidade_ceia_filtrado)

            # configure_plotly_browser_state()
            trace = go.Bar(x=['Café', 'Almoço', 'Lanche', 'Janta', 'Ceia'],
                           y=lista_grafico_filtrado)

            legenda = go.Layout(title='Quantidade de refeições por tipo',
                                xaxis={'title': 'Tipo de Refeição'},
                                yaxis={'title': 'Quantidade'}
                                )
            figura_filtrado = go.Figure(data=trace, layout=legenda)
            st.write(figura_filtrado)