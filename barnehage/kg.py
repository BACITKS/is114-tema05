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

    
    barnehager = pd.read_excel(r'C:\oblig5\is114-tema05\barnehage\kgdata.xlsx', sheet_name='barnehage')
    
    
    valgt_barnehage = form_data.get('liste_over_barnehager_prioritert_5')
    barnehage_info = barnehager[barnehager['barnehage_navn'] == valgt_barnehage]

    
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
    all_data = pd.read_excel(r'C:\oblig5\is114-tema05\barnehage\kgdata.xlsx', sheet_name=None)  # Leser alle ark
    return render_template('commit.html', all_data=all_data)



@app.route('/statistikk', methods=['GET', 'POST'])
def statistikk():
    kommune = None
    chart_html = None
    error = None

    try:
        # Les Excel-filen (behold din eksisterende filbane)
        file_path = r'C:\oblig5\is114-tema05\barnehage\barnehagedata.xlsm'
        df = pd.read_excel(file_path)
        
        # Sett kolonnenavn og fjern overskriftsrader som før
        df.columns = ['Region'] + list(range(2015, 2024))
        df = df.iloc[3:].reset_index(drop=True)
        
        # Hent liste over kommuner for nedtrekkslisten
        kommuner = df['Region'].dropna().unique().tolist()

        # Hvis en kommune er valgt (POST request)
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
                    
                    # Fjern eventuelle ugyldige verdier
                    kommune_data_long = kommune_data_long[kommune_data_long['Prosent'] != '.']
                    kommune_data_long['Prosent'] = pd.to_numeric(kommune_data_long['Prosent'])
                    
                    # Lag alt chart
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
                            kommuner=kommuner)  # Viktig! Send kommunelisten til templaten

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
