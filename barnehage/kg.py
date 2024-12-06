from flask import Flask
from flask import url_for
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from kgmodel import (Foresatt, Barn, Soknad, Barnehage)
from kgcontroller import (form_to_object_soknad, insert_soknad, select_alle_barnehager, select_all_soeknader)
import pandas as pd
import altair as alt
import dbexcel as db



app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY' # nødvendig for session

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/barnehager')
def barnehager():
    information = select_alle_barnehager()
    return render_template('barnehager.html', data=information)

@app.route('/behandle', methods=['POST'])
def behandle():
    form_data = request.form.to_dict()

    # Oppdater søknad i minne via insert_soknad
    from kgcontroller import insert_soknad
    insert_soknad(form_data)

    # Returner svar til brukeren
    valgt_barnehage = form_data.get('liste_over_barnehager_prioritert_5')
    resultat = "TILBUD" if db.barnehage.loc[
        db.barnehage['barnehage_navn'] == valgt_barnehage, 
        'barnehage_ledige_plasser'
    ].iloc[0] > 0 else "AVSLAG"

    return render_template('svar.html', resultat=resultat)


'''
@app.route('/behandle', methods=['POST'])
def behandle():
    form_data = request.form.to_dict()

    # Oppdater søknad i minne via insert_soknad
    from kgcontroller import insert_soknad
    insert_soknad(form_data)

    # Returner svar til brukeren
    valgt_barnehage = form_data.get('liste_over_barnehager_prioritert_5')
    resultat = "TILBUD" if db.barnehage.loc[
        db.barnehage['barnehage_navn'] == valgt_barnehage, 
        'barnehage_ledige_plasser'
    ].iloc[0] > 0 else "AVSLAG"

    return render_template('svar.html', resultat=resultat)
'''

@app.route('/soeknader')
def soeknader():
    soeknader_data = select_all_soeknader()
    return render_template('soeknader.html', soeknader=soeknader_data)


@app.route('/svar')
def svar():
    information = session.get('information', {})
    resultat = session.get('resultat', "AVSLAG")  
    return render_template('svar.html', data=information, resultat=resultat)


@app.route('/commit')
def commit():
    db.commit_all()  # Skriver alle endringer til Excel

    all_data = pd.read_excel(r'C:\oblig5\is114-tema05\barnehage\kgdata.xlsx', sheet_name=None)
    return render_template('commit.html', all_data=all_data['soknad'].to_dict(orient='records'))


@app.route('/statistikk', methods=['GET', 'POST'])
def statistikk():
    kommune = None
    chart_html = None
    error = None

    try:
        
        file_path = r'C:\oblig5\is114-tema05\barnehage\barnehagedata.xlsm'
        df = pd.read_excel(file_path)
        
       
        df.columns = ['Region'] + list(range(2015, 2024))
        df = df.iloc[3:].reset_index(drop=True)
        
       
        kommuner = df['Region'].dropna().unique().tolist()

        
        if request.method == 'POST':
            kommune = request.form.get('kommune')
            if kommune:
                kommune_data = df[df['Region'] == kommune]
                if not kommune_data.empty:
                    kommune_data_long = pd.melt(
                        kommune_data,
                        id_vars=['Region'],
                        value_vars=list(range(2015, 2024)),
                        var_name='År',
                        value_name='Prosent'
                    )
                    
                    #Fjern drittverdier
                    kommune_data_long = kommune_data_long[kommune_data_long['Prosent'] != '.']
                    kommune_data_long['Prosent'] = pd.to_numeric(kommune_data_long['Prosent'])
                    
                    #altair
                    chart = alt.Chart(kommune_data_long).mark_line(
                        point=True,
                        color='green',  # Grønn strek
                        strokeWidth=2   # Tykk strek
                    ).encode(
                        x='År:O',
                        y=alt.Y('Prosent:Q', scale=alt.Scale(domain=[0, 100])),
                        tooltip=['År', 'Prosent']
                    ).properties(
                        title=f'Barnehageprosent i {kommune}',
                        width=800,      # Brede graf
                        height=400      # Høye graf
                    ).configure_axis(
                        labelFont='Arial',
                        titleFont='Arial',
                        labelFontWeight='bold',
                        titleFontWeight='bold'
                    ).configure_title(
                        font='Arial',
                        fontSize=20,
                        fontWeight='bold'
                    )
                    
                    chart_html = chart.to_html()
                else:
                    error = f"Ingen data funnet for {kommune}"

        return render_template('statistikk.html', 
                            kommune=kommune,
                            chart_html=chart_html, 
                            error=error,
                            kommuner=kommuner)  

    except Exception as e:
        error = f"En feil oppstod: {str(e)}"
        return render_template('statistikk.html', error=error, kommuner=[])


@app.route('/soknad')
def soknad():
    # Hent barnehage-listen fra Excel
    barnehager_df = pd.read_excel(r'C:\oblig5\is114-tema05\barnehage\kgdata.xlsx', sheet_name='barnehage')
    barnehager = barnehager_df.to_dict('records')
    return render_template('soknad.html', barnehager=barnehager)


"""
Referanser
[1] https://stackoverflow.com/questions/21668481/difference-between-render-template-and-redirect
"""

"""
Søkeuttrykk

"""
