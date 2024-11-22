from flask import Flask
from flask import url_for
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from kgmodel import (Foresatt, Barn, Soknad, Barnehage)
from kgcontroller import (form_to_object_soknad, insert_soknad, commit_all, select_alle_barnehager, select_all_soeknader)
import pandas as pd
import altair as alt



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

    # Last inn barnehagedata fra Excel
    barnehager = pd.read_excel('kgdata.xlsx', sheet_name='barnehage')
    
    
    valgt_barnehage = form_data.get('liste_over_barnehager_prioritert_5')
    barnehage_info = barnehager[barnehager['barnehage_navn'] == valgt_barnehage]

    # Hvis vi ikke finner barnehagen, returner Avslag umiddelbart
    if barnehage_info.empty:
        return render_template('svar.html', resultat="AVSLAG")
    
    ledige_plasser = barnehage_info['barnehage_ledige_plasser'].values[0]

    # Sjekk fortrinnsrett
    har_fortrinnsrett = any([
        form_data.get('fortrinnsrett_barnevern') == 'on',
        form_data.get('fortrinnsrett_sykdom_i_familien') == 'on',
        form_data.get('fortrinnsrett_sykdome_paa_barnet') == 'on'
    ])

    # Logikken: Tilbud gis bare hvis det er ledige plasser eller fortrinnsrett
    if ledige_plasser > 0 or har_fortrinnsrett:
        resultat = "TILBUD"
    else:
        resultat = "AVSLAG"

    # Returner resultatet til brukeren
    return render_template('svar.html', resultat=resultat)



@app.route('/soeknader')
def soeknader():
    soeknader_data = select_all_soeknader()  
    return render_template('soeknader.html', soeknader=soeknader_data)


@app.route('/svar')
def svar():
    information = session.get('information', {})
    resultat = session.get('resultat', "AVSLAG")  # Hent resultatet fra session
    return render_template('svar.html', data=information, resultat=resultat)


@app.route('/commit')
def commit():
    all_data = pd.read_excel('kgdata.xlsx', sheet_name=None)  # Leser alle ark
    return render_template('commit.html', all_data=all_data)



@app.route('/statistikk', methods=['GET', 'POST'])
def statistikk():
    kommune = None
    chart_html = None
    error = None

    if request.method == 'POST':
        kommune = request.form.get('kommune')

        if kommune:
            try:
                
                data = pd.DataFrame({  
                    'Year': [2021, 2022, 2023],
                    'Percentage': [40, 45, 50]
                })

                chart = alt.Chart(data).mark_line(
                    point=True,
                    strokeWidth=3,
                    color='#1f77b4'
                ).encode(
                    x=alt.X('Year:O', title='År'),
                    y=alt.Y('Percentage:Q', title='Prosentandel', scale=alt.Scale(domain=[0, 100])),
                    tooltip=['Year', 'Percentage']
                ).properties(
                    title={
                        'text': f'Barnehage Prosentandel i {kommune}',
                        'fontSize': 16,
                        'fontWeight': 'bold'
                    },
                    width=600,
                    height=400
                )
                chart_html = chart.to_html()

            except Exception as e:
                error = f"Kunne ikke generere statistikk for {kommune}: {e}"

    return render_template('statistikk.html', kommune=kommune, chart_html=chart_html, error=error)


"""
Referanser
[1] https://stackoverflow.com/questions/21668481/difference-between-render-template-and-redirect
"""

"""
Søkeuttrykk

"""
