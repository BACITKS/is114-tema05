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
        # Process the form data
        form_data = request.form.to_dict()
        insert_soknad(form_data)  # Insert the application
        commit_all()  # Save to kgdata.xlsx
        return redirect(url_for('soeknader'))  # Redirect to applications list

    # Render the application form for GET requests
    return render_template('soknad.html')


@app.route('/soeknader')
def soeknader():
    soeknader_data = select_all_soeknader()  # Fetch applications data
    return render_template('soeknader.html', soeknader=soeknader_data)


@app.route('/svar')
def svar():
    information = session.get('information', {})
    resultat = session.get('resultat', "AVSLAG")  # Hent resultatet fra session
    return render_template('svar.html', data=information, resultat=resultat)


@app.route('/commit')
def commit():
    commit_all()
    return render_template('commit.html')

@app.route('/statistikk', methods=['GET', 'POST'])
def statistikk():
    kommune = None
    chart_html = None
    error = None

    if request.method == 'POST':
        kommune = request.form.get('kommune')

        if kommune:
            try:
                # Replace this with your actual data processing for the selected municipality
                data = pd.DataFrame({  # Example data
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