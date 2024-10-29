from flask import Flask
from flask import url_for
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from kgmodel import (Foresatt, Barn, Soknad, Barnehage)
from kgcontroller import (form_to_object_soknad, insert_soknad, commit_all, select_alle_barnehager)

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY' # nødvendig for session

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/barnehager')
def barnehager():
    information = select_alle_barnehager()
    return render_template('barnehager.html', data=information)

@app.route('/behandle', methods=['GET', 'POST'])
def behandle():
    if request.method == 'POST':
        sd = request.form
        print(sd)
        log = insert_soknad(form_to_object_soknad(sd))
        print(log)
        
        # Legg til logikk
        antall_ledige_plasser = 5 
        fortrinnsrett_grunner = [
            sd.get('fortrinnsrett_barnevern') == 'on',
            sd.get('fortrinnsrett_sykdom_familien') == 'on',
            sd.get('fortrinnsrett_sykdom_barnet') == 'on',
            sd.get('fortrinnsrett_annet') == 'on'
        ]
        har_fortrinnsrett = any(fortrinnsrett_grunner)

        # Bestem resultatet basert på ledige plasser og fortrinnsrett
        if antall_ledige_plasser > 0 or har_fortrinnsrett:
            resultat = "TILBUD"
        else:
            resultat = "AVSLAG"

        session['information'] = sd
        session['resultat'] = resultat  # Lagre resultatet i session
        return redirect(url_for('svar'))
    else:
        return render_template('soknad.html')

import openpyxl

def hent_alle_soeknader():
    workbook = openpyxl.load_workbook('barnehage/kgdata.xlsx')
    sheet = workbook.active
    soeknader = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        soeknad = {
            'navn_foresatt': row[0],
            'adresse': row[1],
            'telefon': row[2],
        }
        soeknader.append(soeknad)

    return soeknader

    
@app.route('/soeknader')
def soeknader():
    soeknader = hent_alle_soeknader()
    antall_ledige_plasser = hent_ledige_plasser()

    for soeknad in soeknader:
        if antall_ledige_plasser > 0:
            soeknad['status'] = "TILBUD"
            antall_ledige_plasser -= 1
        else:
            soeknad['status'] = "AVSLAG"

    return render_template('soeknader.html', soeknader=soeknader)



@app.route('/svar')
def svar():
    information = session.get('information', {})
    resultat = session.get('resultat', "AVSLAG")  # Hent resultatet fra session
    return render_template('svar.html', data=information, resultat=resultat)


@app.route('/commit')
def commit():
    commit_all()
    return render_template('commit.html')




"""
Referanser
[1] https://stackoverflow.com/questions/21668481/difference-between-render-template-and-redirect
"""

"""
Søkeuttrykk

"""