from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from flask import Flask
import pandas as pd
import dash
import numpy as np
import dash_table
import plotly.graph_objects as go
from dash_table import FormatTemplate
from dash.dash_table.Format import Format

# 解説
guide1 = 'democ = 民主主義の度合　　autoc = 独裁政治の程度　　polity = democ - autoc'

server = Flask(__name__)
app = dash.Dash(server=server, external_stylesheets=[dbc.themes.FLATLY])
app.title = 'Dashboard'
#データファイルを読み込む
df1 = pd.read_pickle('pref_kpi.pkl')
df2 = pd.read_pickle('pref_kpi_describe.pkl')
df3 = pd.read_pickle('polity.pkl')
df4 = pd.read_pickle('archigos.pkl')
# Index(['country', 'year', 'democ', 'autoc', 'polity', 'polity2'], dtype='object')
# Index(['obsid', 'ccode', 'idacr', 'leader', 'jch_country', 'ch_country','start_date', 'end_date']
#表示候補の列名のリストを作成する(1)
my_list_1 = df1.columns
to_remove_1 = ['年度','地域コード','都道府県','ch_year','id_pref']
remained_list_1 = [i for i in my_list_1 if i not in to_remove_1]
#表示候補の列名のリストを作成する(2)
my_list_2 = df3.columns
to_remove_2 = ['country','year']
remained_list_2 = [i for i in my_list_2 if i not in to_remove_2]
# 【臨時】コードの仮置き開始
# コードの仮置き終了
# 表示する列を定義する
columns1 = [
    dict(id='obsid',name='obsid'),
    dict(id='leader', name='リーダー名'),
    dict(id='jch_country', name='国名'),
    dict(id='ch_country', name='国名(英語)'),
    dict(id='start_date', name='開始日'),
    dict(id='end_date', name='終了日')
]
# データテーブルを描画する関数を定義する
def create_dash_table(df):
    return dash_table.DataTable(
        data=df.to_dict('records'),
        columns=columns1,
        style_cell={'fontsize':20, 'font-family':'IPAexGothic'},
        style_cell_conditional=[{'if':{'column_id':c},'textAlign':'left'} for c in ['obsid']],
        style_data={'color':'black','backgroundColor':'white'},
        style_data_conditional=[{'if':{'row_index':'odd'},'backgroundColor':'rgb(220,220,220)'}],
        style_header={'backgroundColor':'rgb(210,210,210)','color':'black','fontWeight':'bold'} )
# レイアウトの定義
app.layout = dbc.Container([ 
    dbc.Row(
        dbc.Col(
            html.H2("政治・経済の各種指標"), width={'size': 12, 'offset': 0, 'order': 0}), 
        style = {'textAlign': 'center', 'paddingBottom': '1%'}),
    dbc.Row(
        dbc.Col(
            dcc.Loading(
                children=[
                    html.P('　'),
                    html.H4("世界各国の民主化指標の推移",style={'textDecoration':'underline'}),
                    html.P(guide1),
                    html.Div(
                        dcc.Dropdown(id='dropdown4-country',options=[{'label':i,'value':i} for i in df3['country'].unique()],value='Japan'),
                        style={'width':'30%','display':'inline-block','margin-right':10}),
                    html.Div(
                        dcc.Dropdown(id='dropdown4-kpi',options=[{'label':i,'value':i} for i in remained_list_2],value='polity'),
                        style={'width':'30%','display':'inline-block','margin-right':10}),
                    html.Div(
                        dcc.Dropdown(id='dropdown4-plot',options=[{'label':i,'value':i} for i in ['棒グラフ','折れ線グラフ']],value='棒グラフ'),
                        style={'width':'30%','display':'inline-block','margin-right':10}),
                    dcc.Graph(id='polity-plot')
                    ],color='#000000',type='dot',fullscreen=True ))),
    dbc.Row(
        dbc.Col(
            dcc.Loading(
                children=[
                    html.H4("都道府県の各種指標の分布",style={'textDecoration':'underline'}),
                    html.Div(
                        dcc.Dropdown(id='dropdown1-kpi',options=[{'label':i,'value':i} for i in remained_list_1],value='総人口'),
                        style={'width':'30%','display':'inline-block','margin-right':10}),
                    html.Div(
                        dcc.Dropdown(id='dropdown1-plot',options=[{'label':i,'value':i} for i in ['箱ひげ図','散布図','バイオリン']],value='箱ひげ図'),
                        style={'width':'30%','display':'inline-block','margin-right':10}),
                    dcc.Graph(id='box-plot')
                    ],color='#000000',type='dot',fullscreen=True ))),
    dbc.Row(
        dbc.Col(
            dcc.Loading(
                children=[
                    html.H4("特定都道府県の指標の推移",style={'textDecoration':'underline'}),
                    html.Div(
                        dcc.Dropdown(id='dropdown2-pref',options=[{'label':i,'value':i} for i in df1['都道府県'].unique()],value='東京都'),
                        style={'width':'30%','display':'inline-block','margin-right':10}),
                    html.Div(
                        dcc.Dropdown(id='dropdown2-kpi',options=[{'label':i,'value':i} for i in remained_list_1],value='総人口'),
                        style={'width':'30%','display':'inline-block','margin-right':10}),
                    html.Div(
                        dcc.Dropdown(id='dropdown2-plot',options=[{'label':i,'value':i} for i in ['棒グラフ','折れ線グラフ']],value='折れ線グラフ'),
                        style={'width':'30%','display':'inline-block','margin-right':10}),
                    dcc.Graph(id='basic-plot')
                    ],color='#000000',type='dot',fullscreen=True ))),
    dbc.Row(
        dbc.Col(
            dcc.Loading(
                children=[
                    html.H4("世界の国別リーダーの変遷",style={'textDecoration':'underline'}),
                    html.Div(
                        dcc.Dropdown(id='dropdown3-country',options=[{'label':i,'value':i} for i in df4['jch_country'].unique()],value='日本国'),
                        style={'width':'30%','display':'inline-block','margin-right':10}),
                    html.Div(id='datatable-paging',children=[])
                    ],color='#000000',type='dot',fullscreen=True )))
])
# グラフ1（分布グラフ）のコールバックと実行関数の記述
@app.callback(
    Output('box-plot','figure'),
    [Input('dropdown1-kpi','value'),Input('dropdown1-plot','value')])
def update_figure(inval1,inval2):
    filtered_df=df1
    if inval2 == '箱ひげ図':
        fig=px.box(filtered_df,x='ch_year',y=inval1,hover_name='都道府県',template="ggplot2")
        fig.update_layout(transition_duration=500)
        return fig
    elif inval2 == '散布図':
        fig=px.scatter(filtered_df,x='ch_year',y=inval1,hover_name='都道府県',template="ggplot2")
        fig.update_layout(transition_duration=500)
        return fig
    else:
        fig=px.violin(filtered_df,x='ch_year',y=inval1,hover_name='都道府県',template="ggplot2")
        fig.update_layout(transition_duration=500)
        return fig
    return
# グラフ2（基本グラフ）のコールバックと実行関数の記述
@app.callback(
    Output('basic-plot','figure'),
    [Input('dropdown2-pref','value'),Input('dropdown2-kpi','value'),Input('dropdown2-plot','value')])
def update_figure(inval1,inval2,inval3):
    if inval3 == '棒グラフ':
        filtered_df=df1[df1['都道府県']==inval1]
        fig=px.bar(filtered_df,x='ch_year',y=inval2,template="ggplot2")
        fig.update_layout(transition_duration=500)
        return fig
    else:
        df4 = df1[df1['都道府県']==inval1]
        filtered_df = pd.concat([df2,df4])
        fig=px.line(filtered_df,x='ch_year',y=inval2,color='都道府県',markers=True,template="ggplot2")
        fig.update_layout(transition_duration=500)
        return fig

# グラフ3（データテーブル）のコールバックと実行関数の記述
@app.callback(
    Output('datatable-paging','children'),
    [Input('dropdown3-country','value')])
def update_table(inval1):
    df502=df4[df4['jch_country'] == inval1 ]
    return create_dash_table(df502)

# グラフ4（国際政治グラフ）のコールバックと実行関数の記述
@app.callback(
    Output('polity-plot','figure'),
    [Input('dropdown4-country','value'),Input('dropdown4-kpi','value'),Input('dropdown4-plot','value')])
def update_figure(inval1,inval2,inval3):
    filtered_df=df3[df3['country']==inval1]
    if inval3 == '棒グラフ':
        fig=px.bar(filtered_df,x='year',y=inval2)
        fig.update_layout(transition_duration=500)
        return fig
    else:
        fig=px.line(filtered_df,x='year',y=inval2)
        fig.update_layout(transition_duration=500)
        return fig

if __name__=='__main__':
    app.run_server()
