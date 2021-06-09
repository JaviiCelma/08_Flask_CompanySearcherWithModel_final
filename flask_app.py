
# A very simple Flask Hello World app for you to get started with...

from flask import Flask,render_template, request

app = Flask(__name__)


import sqlite3
conn = sqlite3.connect('./database/company_balancesheet_database.db')
import pandas as pd
pd.set_option('display.float_format', lambda x: '%.3f' % x)
df = pd.read_sql("""
 SELECT *
    FROM cuentas_anuales
""", conn)

df.drop('id',inplace=True,axis=1)

df.columns = ['NIF', 'Nombre', 'CNAE',
	   'Total Activos - 2017', 'Total Activos - 2016',
	   'Total Activos - 2015', 'Recursos Propios - 2017', 'Recursos Propios - 2016',
	   'Recursos Propios - 2015', 'Deuda a Corto - 2017',
	   'Deuda a Corto - 2016', 'Deuda a Corto - 2015',
	   'Deuda a Largo - 2017', 'Deuda a Largo - 2016',
	   'Deuda a Largo - 2015', 'Ingresos - 2017',
	   'Ingresos - 2016', 'Ingresos - 2015',
	   'Amortizacion - 2017', 'Amortizacion - 2014',
	   'Amortizacion - 2015', 'Beneficio - 2017', 'Beneficio - 2016',
	   'Beneficio - 2015', 'Estado']

import numpy as np
from joblib import load
modelo=load('Rating_RandomForestClassifier.joblib')
@app.route('/')
def index():
    return render_template('index.html',df=df,ids=list(range(len(df))))

@app.route('/buscador')
def buscador():
    data=df[df['NIF']==request.args['nif']].head(1)
    if 'modelo' in request.args:
        # df['ebitda_income'] = (df.p49100_Profit_h1+df.p40800_Amortization_h1)/(df.p40100_40500_SalesTurnover_h1)
        data['ebitda_income']=(data['Beneficio - 2017']+data['Amortizacion - 2017'])/data['Ingresos - 2017']
        # df['debt_ebitda'] =(df.p31200_ShortTermDebt_h1 + df.p32300_LongTermDebt_h1) /(df.p49100_Profit_h1+df.p40800_Amortization_h1)
        data['debt_ebitda']=(data['Deuda a Corto - 2017']+data['Deuda a Largo - 2017'])/(data['Beneficio - 2017']+data['Amortizacion - 2017'])
        # df['rraa_rrpp'] = (df.p10000_TotalAssets_h1 - df.p20000_OwnCapital_h1) /df.p20000_OwnCapital_h1
        data['rraa_rrpp']=(data['Total Activos - 2017']-data['Recursos Propios - 2017'])/data['Recursos Propios - 2017']
        # df['log_operating_income'] = np.log(df.p40100_40500_SalesTurnover_h1)
        data['log_operating_income']=np.log(data['Ingresos - 2017'])
        data=data.replace([np.inf, -np.inf], np.nan).fillna(0)
        X = data[['ebitda_income','debt_ebitda','rraa_rrpp','log_operating_income']]
        data['probabilidad_default']=modelo.predict_proba(X)[:,1]
    if 'JSON' in request.args:
        return data.to_json(orient='records')
    else:
        data_html= data.T.to_html()
        return render_template('index.html',result=1,data=data_html,df=df,ids=list(range(len(df))))
