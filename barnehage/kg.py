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
    workbook = openpyxl.load_workbook(r"C:\oblig5\is114-tema05\barnehage\kgdata.xlsx")
    sheet = workbook.active
    soeknader = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        soeknad = {
            'barnehage_id': row[0],      # Assuming the first column is the daycare ID
            'navn_foresatt': row[1],     # Second column is the applicant's name
            'adresse': row[2],           # Third column is the address
            'telefon': row[3],           
        }
        soeknader.append(soeknad)

    return soeknader

def hent_alle_barnehager():
    workbook = openpyxl.load_workbook('C:\\oblig5\\is114-tema05\\barnehage\\kgdata.xlsx')
    sheet = workbook.active
    barnehager = []

    for row in sheet.iter_rows(min_row=2, values_only=True):
        barnehage = {
            'id': row[0],                        # ID
            'navn': row[1],                      # Navn
            'antall_plasser': row[2],            # Total # plasser
            'antall_ledige_plasser': row[3],     # tilgjengelige plasser
        }
        barnehager.append(barnehage)

    return barnehager
    
@app.route('/soeknader')
def soeknader():
    # Define the daycare centers with their available spots
    barnehager = [
        {'id': 1, 'navn': 'Sunshine Preschool', 'antall_plasser': 50, 'antall_ledige_plasser': 15},
        {'id': 2, 'navn': 'Happy Days Nursery', 'antall_plasser': 25, 'antall_ledige_plasser': 2},
        {'id': 3, 'navn': '123 Learning Center', 'antall_plasser': 35, 'antall_ledige_plasser': 4},
        {'id': 4, 'navn': 'ABC Kindergarten', 'antall_plasser': 12, 'antall_ledige_plasser': 0},
        {'id': 5, 'navn': 'Tiny Tots Academy', 'antall_plasser': 15, 'antall_ledige_plasser': 5},
        {'id': 6, 'navn': 'Giggles and Grins Childcare', 'antall_plasser': 10, 'antall_ledige_plasser': 0},
        {'id': 7, 'navn': 'Playful Pals Daycare', 'antall_plasser': 40, 'antall_ledige_plasser': 6},
    ]

    # Fetch applications, with each application specifying the desired daycare
    soeknader = hent_alle_soeknader()

    for soeknad in soeknader:
        barnehage_id = soeknad.get('barnehage_id')

        # Find the specific daycare the application is targeting
        valgt_barnehage = next((b for b in barnehager if b['id'] == barnehage_id), None)

        if valgt_barnehage and valgt_barnehage['antall_ledige_plasser'] > 0:
            # Assign "TILBUD" status and decrement available spots
            soeknad['status'] = "TILBUD"
            valgt_barnehage['antall_ledige_plasser'] -= 1
        else:
            # Assign "AVSLAG" if no spots are available
            soeknad['status'] = "AVSLAG"

    # Render the results in the soeknader.html template
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