#importe dos pacotes
import streamlit as st
import pandas as pd
from PIL import Image
import  time
import base64
import plotly.graph_objs as go
import numpy as np
import limpeza

#carrega logo do empresa
image = Image.open('logo-grupo-sococo.png')
st.image(image,width=700 , caption='Cálculo de Refeições Extras')

#st.set_option('deprecation.showfileUploaderEncoding', False)
empresa = st.selectbox("Selecione a empresa",
                ('SOCOCO', 'ACQUA', 'AMAFIBRA'))

#recebe o arquivo de texto do usuário
uploaded_file = st.file_uploader("Selecione ou arraste seu arquivo gerado pelo DATASUL: ",
                                 type="txt", encoding="windows-1252")
#formata o arquivo recebido em 06 colunas
colunas = [5,11,28,12,7,7]

if uploaded_file is not None:
# se o arquivo foi carregado, le o arquivo e gera um novo arquivo formatado
    data = pd.read_fwf(uploaded_file, widths=colunas, header=None)
    data.to_csv('arquivo_sem_tratamento.txt', index=False)

    # Inicia a primeira limpeza do arquivo gerado acima.
    if empresa == 'SOCOCO':
        limpeza.limpeza_sococo()
    elif empresa == 'ACQUA':
        limpeza.limpeza_acqua()
    else:
        limpeza.limpeza_amafibra()

#carrega arquivo da segunda limpeza e gera o arquivo final limpo para mostrar na tela
    df = pd.read_csv('segunda_limpeza.txt', sep=',')
    df.columns = ['Empresa', 'Matricula', 'Funcionario', 'Data', 'Hora', 'Refeicao']
    df.to_csv('arquivo_limpo.txt', index=False)

    with st.spinner('Aguarde o carregamento do arquivo...'):
        time.sleep(5)

    if st.checkbox('Base de Refeição Tratada'):
        #trasnformar categoria REFEICAO para fator
        #(ALMOÇO - 0/1	CAFE- 0/1	CEIA- 0/1	JANTAR- 0/1	LANCHE- 0/1)
        filtro_ref = pd.get_dummies(df['Refeicao'])
        filtro_ref.columns=['ALMOCO','CAFE','CEIA','JANTAR','LANCHE']
        #concatena df inicial com novas colunas geradas pelo fator
        novo_df = pd.concat([df, filtro_ref], axis=1, sort=False)

        #remove as colunas (Empresa , Hora , Refeicao) para melhor visualizacao
        novo_df2 = novo_df.drop(columns=['Empresa','Hora','Refeicao'])
        #Cria a base para gerar o relatorio diario
        relatorio_diario = novo_df.drop(columns=['Empresa','Matricula','Funcionario','Hora','Refeicao'])
        relatorio_diario = relatorio_diario.groupby(['Data']).sum()
        relatorio_diario = relatorio_diario.reset_index(level=['Data'])

        # criar indice para agrupar refeicoes por dia
        # 'estilo' contador para adiconar preco diferente
        mat_dia = novo_df2.groupby(['Matricula','Funcionario','Data']).sum()


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
            (mat_dia['ALMOCO'] == 1) & (mat_dia['CEIA'] == 0) & (mat_dia['JANTAR'] == 0),
            (mat_dia['ALMOCO'] == 1) & (mat_dia['CEIA'] == 1) & (mat_dia['JANTAR'] == 1),
            (mat_dia['ALMOCO'] == 1) & (mat_dia['CEIA'] == 1) & (mat_dia['JANTAR'] == 0),
            (mat_dia['ALMOCO'] == 1) & (mat_dia['CEIA'] == 0) & (mat_dia['JANTAR'] == 1),
            (mat_dia['ALMOCO'] > 1) & (mat_dia['CEIA'] == 0) & (mat_dia['JANTAR'] == 0),
            (mat_dia['ALMOCO'] > 1) & (mat_dia['CEIA'] != 0) | (mat_dia['JANTAR'] != 0),
            (mat_dia['ALMOCO'] == 0) & (mat_dia['CEIA'] != 0) | (mat_dia['JANTAR'] != 0)]
        # escolhas de acordo com a lista de desconto ocorrida
        choices = [0.0,
                   (mat_dia['ALMOCO'] * 8.85 + mat_dia['CEIA'] * 8.85 + mat_dia['JANTAR'] * 8.85) - 8.85,
                   (mat_dia['ALMOCO'] * 8.85 + mat_dia['CEIA'] * 8.85 + mat_dia['JANTAR'] * 8.85) - 8.85,
                   (mat_dia['ALMOCO'] * 8.85 + mat_dia['CEIA'] * 8.85 + mat_dia['JANTAR'] * 8.85) - 8.85,
                   (mat_dia['ALMOCO'] * 8.85) - 8.85,
                   (mat_dia['ALMOCO'] * 8.85 + mat_dia['CEIA'] * 8.85 + mat_dia['JANTAR'] * 8.85) - 8.85,
                   (mat_dia['ALMOCO'] * 0 + mat_dia['CEIA'] * 8.85 + mat_dia['JANTAR'] * 8.85) - 8.85]

        #soma de valores na coluna DESCONTAR
        mat_dia['NUM_REFEICOES'] = mat_dia['ALMOCO'] + mat_dia['CAFE']+ mat_dia['CEIA']+ \
                               mat_dia['JANTAR']+ mat_dia['LANCHE']

        mat_dia['DESCONTO_1'] = calculo_cafe + calculo_lanche
        mat_dia['DESCONTO_2'] = np.select(conditions, choices, default=0.0)
        st.markdown('Refeições por funcionário')
        st.write(mat_dia)
        st.write("Linha / Colunas: ", novo_df2.shape)

        st.markdown('Quantidade de Refeições Diária ')
        st.write(relatorio_diario)
        st.write("Linha / Colunas: ", relatorio_diario.shape)

        # Filtro para saber quem teve refeicoes em excesso.
        filtrado = mat_dia.loc[(mat_dia['NUM_REFEICOES'] >= 3) | (mat_dia['ALMOCO']==2) |(mat_dia['CAFE']==2) |
                               (mat_dia['CEIA']==2) |  (mat_dia['JANTAR']==2) | (mat_dia['LANCHE']==2) ]

        filtrado['DESCONTO_TOTAL'] = mat_dia['DESCONTO_1'] + mat_dia['DESCONTO_2']
        filtrado.DESCONTO_2 = filtrado.DESCONTO_2.round(2)
        filtrado.DESCONTO_TOTAL = filtrado.DESCONTO_TOTAL.round(2)

        st.markdown('Relação de Funcionário com Refeições EXTRAS')
        st.write(filtrado)
        st.write("Linha / Colunas: ", filtrado.shape)


        #Organizando para contacter base de dados tratato
        base_tratada = filtrado.reset_index(level=['Matricula', 'Funcionario', 'Data'])
        base_tratada = pd.concat([base_tratada, df, relatorio_diario], ignore_index=True, axis=1, sort=False)
        base_tratada.columns = ['MATRICULA','FUNCIONARIO','DATA','ALMOCO','CAFE','CEIA',
                               'JANTAR','LANCHE','NUM_REFEICAO','DESCONTO_1','DESCONTO_2','DESCONTO_TOTAL',
                              'EMPRESA', 'MATRICULA','FUNCIONARIO', 'DATA', 'HORA', 'REFEICAO',
                              'DATA','ALMOCO','CAFE','CEIA','JANTAR','LANCHE']
        #salva o arquivo em formato de texto com os INDÍCES para download
        base_tratada.to_csv('base_tratada.txt',index=False)


        #funcao para gerar downlod da data frame tratado
        def download_link(object_to_download, download_filename, download_link_text):

            if isinstance(object_to_download, pd.DataFrame):
                object_to_download = object_to_download.to_csv(index=True)
                b64 = base64.b64encode(object_to_download.encode()).decode()
                return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


        tmp_download_link = download_link(base_tratada, 'base_tratada.txt', 'Clique para salvar o arquivo')
        st.markdown(tmp_download_link, unsafe_allow_html=True)

#----------------------------------------------------------#
        #Gráfico numero de refeicoes
    if st.checkbox('Gráfico de Quantidade de Refeições'):
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
                       y=lista_grafico,
                       text=lista_grafico,
                       textposition='auto')

        legenda = go.Layout(title='Quantidade de refeições por tipo',
                            xaxis={'title': 'Tipo de Refeição'},
                            yaxis={'title': 'Quantidade'}
                            )
        figura = go.Figure(data=trace, layout=legenda)
        st.write(figura)

#-------------------------------------------------------------------------#
        #Gráfico de reficoes extras
        if st.checkbox('Gráfico de Quantidade EXTRA de Refeições'):
            quantidade_cafe_filtrado = sum(filtrado['CAFE'])
            quantidade_almoco_filtrado = sum(filtrado['ALMOCO'])
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
                           y=lista_grafico_filtrado,
                           text=lista_grafico_filtrado,
                           textposition='auto')

            legenda = go.Layout(title='Quantidade de refeições por tipo',
                                xaxis={'title': 'Tipo de Refeição'},
                                yaxis={'title': 'Quantidade'}
                                )
            figura_filtrado = go.Figure(data=trace, layout=legenda)
            st.write(figura_filtrado)
