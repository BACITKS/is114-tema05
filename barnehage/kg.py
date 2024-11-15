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

from kgcontroller import form_to_object_soknad, insert_soknad, commit_all

@app.route('/behandle', methods=['GET', 'POST'])
def behandle():
    if request.method == 'POST':
        form_data = request.form.to_dict()
        
        # Logic to determine if the user gets a TILBUD or AVSLAG
        antall_ledige_plasser = 5  # Placeholder for available spots, replace with actual logic if available
        har_fortrinnsrett = any([
            form_data.get('fortrinnsrett_barnevern') == 'on',
            form_data.get('fortrinnsrett_sykdom_familien') == 'on',
            form_data.get('fortrinnsrett_sykdom_barnet') == 'on',
            form_data.get('fortrinnsrett_annet') == 'on'
        ])
        
        # Determine the result based on available spots and priority
        if antall_ledige_plasser > 0 or har_fortrinnsrett:
            resultat = "TILBUD"
        else:
            resultat = "AVSLAG"
        
        # Insert application and save to Excel
        insert_soknad(form_data)
        commit_all()

        return render_template('svar.html', resultat=resultat)
    
    return render_template('soknad.html') 


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
    from kgcontroller import select_all_soeknader 
    all_data = select_all_soeknader()  
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

                chart = alt.Chart(data).mark_line().encode(
                    x='Year:O',
                    y='Percentage:Q'
                ).properties(
                    title=f"Barnehage Prosentandel i {kommune}"
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
