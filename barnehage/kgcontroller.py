# kgcontroller module
import pandas as pd
import numpy as np
from dbexcel import *
from kgmodel import *


# CRUD metoder

# Create
# pd.append, pd.concat eller df.loc[-1] = [1,2] df.index = df.index + 1 df = df.sort_index()
def insert_foresatt(f):
    # Ikke en god praksis å oppdaterer DataFrame ved enhver endring!
    # DataFrame er ikke egnet som en databasesystem for webapplikasjoner.
    # Vanligvis bruker man databaseapplikasjoner som MySql, Postgresql, sqlite3 e.l.
    # 3 fremgangsmåter for å oppdatere DataFrame:
    # (1) df.colums er [['a', 'b']]
    #     df = pd.concat([pd.DataFrame([[1,2]], columns=df.columns), df], ignore_index=True)
    # (2) df = df.append({'a': 1, 'b': 2}, ignore_index=True)
    # (3) df.loc[-1] = [1,2]
    #     df.index = df.index + 1
    #     df = df.sort_index()
    global forelder
    new_id = 0
    if forelder.empty:
        new_id = 1
    else:
        new_id = forelder['foresatt_id'].max() + 1
    
    # skriv kode for å unngå duplikater
    
    forelder = pd.concat([pd.DataFrame([[new_id,
                                        f.foresatt_navn,
                                        f.foresatt_adresse,
                                        f.foresatt_tlfnr,
                                        f.foresatt_pnr]],
                columns=forelder.columns), forelder], ignore_index=True)
    
    
    return forelder

def insert_barn(b):
    global barn
    new_id = 0
    if barn.empty:
        new_id = 1
    else:
        new_id = barn['barn_id'].max() + 1
    
    # burde også sjekke for samme foresatt_pnr for å unngå duplikater
    
    barn = pd.concat([pd.DataFrame([[new_id,
                                    b.barn_pnr]],
                columns=barn.columns), barn], ignore_index=True)
    
    return barn


import pandas as pd

def insert_soknad(form_data):
    global soknad, barnehage
    
    excel_path = r'C:\oblig5\is114-tema05\barnehage\kgdata.xlsx'
    
    # Finn nytt søknads-ID
    new_id = 1 if soknad.empty else soknad['sok_id'].max() + 1
    
    # Sjekk om barnehagen har ledige plasser
    valgt_barnehage = form_data.get('liste_over_barnehager_prioritert_5')
    try:
        ledige_plasser = barnehage.loc[
            barnehage['barnehage_navn'] == valgt_barnehage, 
            'barnehage_ledige_plasser'
        ].iloc[0]
    except:
        ledige_plasser = 0  # Hvis barnehagen ikke finnes
    
    # Bestem status basert på ledige plasser
    status = 1 if ledige_plasser > 0 else 0
    
    # Opprett en ny rad med data
    new_row = pd.DataFrame([[
        new_id,
        form_data.get('navn_forelder_1'),
        form_data.get('navn_forelder_2', ''),
        form_data.get('personnummer_barnet_1'),
        form_data.get('fortrinnsrett_barnevern') == 'on',
        form_data.get('fortrinnsrett_sykdom_i_familien') == 'on',
        form_data.get('fortrinnsrett_sykdome_paa_barnet') == 'on',
        form_data.get('fortrinssrett_annet', ''),
        valgt_barnehage,
        form_data.get('har_sosken_som_gaar_i_barnehagen') == 'on',
        form_data.get('tidspunkt_for_oppstart'),
        form_data.get('brutto_inntekt_husholdning'),
        status  # Legg til status
    ]], columns=list(soknad.columns) + ['status'])

    # Oppdater søknader
    soknad = pd.concat([new_row, soknad], ignore_index=True)
    
    # Oppdater antall ledige plasser hvis søknaden godkjennes
    if status == 1:
        barnehage.loc[
            barnehage['barnehage_navn'] == valgt_barnehage, 
            'barnehage_ledige_plasser'
        ] -= 1
    
    # Lagre endringene
    try:
        with pd.ExcelWriter(excel_path, mode='a', if_sheet_exists='replace') as writer:
            soknad.to_excel(writer, sheet_name='soknad', index=False)
            barnehage.to_excel(writer, sheet_name='barnehage', index=False)
        print("Data er lagret!")
        return status
    except Exception as e:
        print(f"Feil ved lagring til Excel: {e}")
        return 0




'''
def insert_soknad(s):
    """[sok_id, foresatt_1, foresatt_2, barn_1, fr_barnevern, fr_sykd_familie,
    fr_sykd_barn, fr_annet, barnehager_prioritert, sosken__i_barnehagen,
    tidspunkt_oppstart, brutto_inntekt]
    """
    global soknad
    new_id = 0
    if soknad.empty:
        new_id = 1
    else:
        new_id = soknad['sok_id'].max() + 1
    
    
    # burde også sjekke for duplikater
    
    soknad = pd.concat([pd.DataFrame([[new_id,
                                     s.foresatt_1.foresatt_id,
                                     s.foresatt_2.foresatt_id,
                                     s.barn_1.barn_id,
                                     s.fr_barnevern,
                                     s.fr_sykd_familie,
                                     s.fr_sykd_barn,
                                     s.fr_annet,
                                     s.barnehager_prioritert,
                                     s.sosken__i_barnehagen,
                                     s.tidspunkt_oppstart,
                                     s.brutto_inntekt]],
                columns=soknad.columns), soknad], ignore_index=True)
    
    return soknad
'''
# ---------------------------
# Read (select)

def select_alle_barnehager():
    """Returnerer en liste med alle barnehager definert i databasen dbexcel."""
    return barnehage.apply(lambda r: Barnehage(r['barnehage_id'],
                             r['barnehage_navn'],
                             r['barnehage_antall_plasser'],
                             r['barnehage_ledige_plasser']),
         axis=1).to_list()

def select_foresatt(f_navn):
    """OBS! Ignorerer duplikater"""
    series = forelder[forelder['foresatt_navn'] == f_navn]['foresatt_id']
    if series.empty:
        return np.nan
    else:
        return series.iloc[0] # returnerer kun det første elementet i series

def select_barn(b_pnr):
    """OBS! Ignorerer duplikater"""
    series = barn[barn['barn_pnr'] == b_pnr]['barn_id']
    if series.empty:
        return np.nan
    else:
        return series.iloc[0] # returnerer kun det første elementet i series
    
    
# --- Skriv kode for select_soknad her
'''
"""Hente fra databasen"""
    
    return soknad.apply(lambda r: {
        'navn_foresatt': r['foresatt_1'],  
        'adresse': r['foresatt_adresse'],
        'telefon': r['foresatt_tlf'],
        'barnehage_navn': r['barnehage_prioritert'],  
        'status': "TILBUD" if r['status'] == 1 else "AVSLAG"  
    }, axis=1).to_list()
'''

# ------------------
# Update

def select_all_soeknader():
    try:
        excel_path = r'C:\oblig5\is114-tema05\barnehage\kgdata.xlsx'
        
        # Les data fra Excel
        soknad_data = pd.read_excel(excel_path, sheet_name='soknad')
        
        # Hvis status-kolonnen ikke finnes, legg den til
        if 'status' not in soknad_data.columns:
            soknad_data['status'] = 0  # Standard verdi er avslag
        
        # Konverter til liste av ordbøker
        soeknader = []
        for _, row in soknad_data.iterrows():
            soeknader.append({
                'soeknadsnummer': row['sok_id'],
                'navn_foresatt': row['foresatt_1'],
                'adresse': row.get('adresse_forelder_1', 'Ikke oppgitt'),
                'barnehage_navn': row['barnehager_prioritert'],
                'status': "TILBUD" if row.get('status', 0) == 1 else "AVSLAG"
            })
        
        return soeknader
    except Exception as e:
        print(f"Feil ved lesing av søknader: {e}")
        return []


# ------------------
# Delete


# ----- Persistent lagring ------
def commit_all():
    """Skriver alle dataframes til excel"""
    with pd.ExcelWriter('kgdata.xlsx', mode='a', if_sheet_exists='replace') as writer:  
        forelder.to_excel(writer, sheet_name='foresatt')
        barnehage.to_excel(writer, sheet_name='barnehage')
        barn.to_excel(writer, sheet_name='barn')
        soknad.to_excel(writer, sheet_name='soknad')
        
# --- Diverse hjelpefunksjoner ---
def form_to_object_soknad(sd):
    """sd - formdata for soknad, type: ImmutableMultiDict fra werkzeug.datastructures
Eksempel:
ImmutableMultiDict([('navn_forelder_1', 'asdf'),
('navn_forelder_2', ''),
('adresse_forelder_1', 'adf'),
('adresse_forelder_2', 'adf'),
('tlf_nr_forelder_1', 'asdfsaf'),
('tlf_nr_forelder_2', ''),
('personnummer_forelder_1', ''),
('personnummer_forelder_2', ''),
('personnummer_barnet_1', '234341334'),
('personnummer_barnet_2', ''),
('fortrinnsrett_barnevern', 'on'),
('fortrinnsrett_sykdom_i_familien', 'on'),
('fortrinnsrett_sykdome_paa_barnet', 'on'),
('fortrinssrett_annet', ''),
('liste_over_barnehager_prioritert_5', ''),
('tidspunkt_for_oppstart', ''),
('brutto_inntekt_husholdning', '')])
    """
    # Lagring i hurtigminne av informasjon om foreldrene (OBS! takler ikke flere foresatte)
    foresatt_1 = Foresatt(0,
                          sd.get('navn_forelder_1'),
                          sd.get('adresse_forelder_1'),
                          sd.get('tlf_nr_forelder_1'),
                          sd.get('personnummer_forelder_1'))
    insert_foresatt(foresatt_1)
    foresatt_2 = Foresatt(0,
                          sd.get('navn_forelder_2'),
                          sd.get('adresse_forelder_2'),
                          sd.get('tlf_nr_forelder_2'),
                          sd.get('personnummer_forelder_2'))
    insert_foresatt(foresatt_2) 
    
    # Dette er ikke elegang; kunne returnert den nye id-en fra insert_ metodene?
    foresatt_1.foresatt_id = select_foresatt(sd.get('navn_forelder_1'))
    foresatt_2.foresatt_id = select_foresatt(sd.get('navn_forelder_2'))
    
    # Lagring i hurtigminne av informasjon om barn (OBS! kun ett barn blir lagret)
    barn_1 = Barn(0, sd.get('personnummer_barnet_1'))
    insert_barn(barn_1)
    barn_1.barn_id = select_barn(sd.get('personnummer_barnet_1'))
    
    # Lagring i hurtigminne av all informasjon for en søknad (OBS! ingen feilsjekk / alternativer)
        
    sok_1 = Soknad(0,
                   foresatt_1,
                   foresatt_2,
                   barn_1,
                   sd.get('fortrinnsrett_barnevern'),
                   sd.get('fortrinnsrett_sykdom_i_familien'),
                   sd.get('fortrinnsrett_sykdome_paa_barnet'),
                   sd.get('fortrinssrett_annet'),
                   sd.get('liste_over_barnehager_prioritert_5'),
                   sd.get('har_sosken_som_gaar_i_barnehagen'),
                   sd.get('tidspunkt_for_oppstart'),
                   sd.get('brutto_inntekt_husholdning'))
    
    return sok_1

# Testing
def test_df_to_object_list():
    assert barnehage.apply(lambda r: Barnehage(r['barnehage_id'],
                             r['barnehage_navn'],
                             r['barnehage_antall_plasser'],
                             r['barnehage_ledige_plasser']),
         axis=1).to_list()[0].barnehage_navn == "Sunshine Preschool"