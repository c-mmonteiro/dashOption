# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from dash import Dash, html, dcc, Input, Output
from dash import dash_table as dt
import plotly.express as px
import pandas as pd

from dadosMt5.dadosMt5 import *

import MetaTrader5 as mt5



app = Dash(__name__)

################################################
####### Dados


dados_ativo = dadosMt5('NULL', 30)

################################################



##################################################
######## Layout

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(
        html.Table(children=[
            html.Tr(children=[
                html.Td(children=[
                    html.Div(
                        id='textarea-example-output',
                        style={'whiteSpace': 'pre-line'}
                    ),
                    dcc.Textarea(
                    id='textarea-example',
                    value='',
                    style={'width': 75, 'height': 15}
                    )
                ]),
                html.Td(children=[
                    dcc.Dropdown(
                        ['Ambas','CALL', 'PUT'],
                        'Ambas',
                        id='tipo-opcao-dorpdown',
                        style={'width': 75, 'height': 30},
                        clearable=False,
                        multi=False
                    )
                ]),
                html.Td(children=[
                    html.Div(
                        'Vencimento'
                    ),
                    dcc.Checklist(['20/01/2023', '21/02/2023'], ['20/01/2023'],
                    id='checkList-vencimento-opcao',
                    inline=True)
                ])
            ])
        ])
    ),

    html.Div(
        id='div-dados-output',
    ),
    dcc.Store(id='intermediate-value')
])

##################################################
### Call Back
@app.callback(
    Output('textarea-example-output', 'children'),
    Output('div-dados-output', 'children'),
    Output('checkList-vencimento-opcao', 'options'),
    Output('checkList-vencimento-opcao', 'value'),
    Input('textarea-example', 'value'),
    Input('tipo-opcao-dorpdown', 'value'),
    Input('checkList-vencimento-opcao', 'value')
)
def update_output(ativoBase, tipoOpcao, vencimento):
    global dados_ativo
    if dados_ativo.get_ativoBase() == ativoBase:

        lista_vencimentos = dados_ativo.get_vencimentos()["Vencimento"].to_list()

        df = pd.DataFrame(columns=['Codigo', 'Strike', 'Ultimo', 'Tipo', 'Estilo', 'P Compra', 'P Venda', 'Vencimento'])

        for idx, venc in enumerate(lista_vencimentos):

            if venc in vencimento:
                dados_ativo.atualiza_dados(idx, 0, "COMPLETO")
                df = pd.concat([df, dados_ativo.get_opcoes()])

        df = df.sort_values(by="Strike")
        df = df.reset_index()

        if tipoOpcao != "Ambas":
            df = df[df['Tipo'] == tipoOpcao]


        print(df)#TODO: está criando um index
        #TODO: Verificar como fazer para ler quando acionar todos os vencimentos
        tabela = dt.DataTable(df[df.columns[1:]].to_dict('records'), [{"name": i, "id": i} for i in df.columns[1:]])

        lista_vencimentos = dados_ativo.get_vencimentos()["Vencimento"].to_list()

        return f'Ação escolhida: {dados_ativo.get_ativoBase()}', tabela, lista_vencimentos, vencimento


    else:
        if (len(ativoBase) == 5 or len(ativoBase) == 6):
            mt5.initialize()
            info = mt5.symbol_info(ativoBase)
            mt5.shutdown()

            if not info:
                return f'Ação invalida!', '', [], []
            else:
                dados_ativo = dadosMt5(ativoBase, 30)#TODO: tornar o numero de dias variavel
                dados_ativo.atualiza_dados(0, 0, "COMPLETO")
                df = dados_ativo.get_opcoes()
                tabela = dt.DataTable(df[df.columns[1:]].to_dict('records'), [{"name": i, "id": i} for i in df.columns[1:]])

                lista_vencimentos = dados_ativo.get_vencimentos()["Vencimento"].to_list()

                return f'Ação escolhida: {ativoBase}', tabela, lista_vencimentos, [lista_vencimentos[0]]
        else:
            return f'Ação invalida!', '', [], []

#################################################
## Funções   

    



##################################################

if __name__ == '__main__':
    app.run_server(debug=True)