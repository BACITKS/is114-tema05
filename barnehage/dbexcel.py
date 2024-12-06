# dbexcel module
import pandas as pd



kgdata = pd.ExcelFile(r'C:\oblig5\is114-tema05\barnehage\kgdata.xlsx')
barnehage = pd.read_excel(kgdata, 'barnehage', index_col=0)
forelder = pd.read_excel(kgdata, 'foresatt', index_col=0)
barn = pd.read_excel(kgdata, 'barn', index_col=0)
soknad = pd.read_excel(kgdata, 'soknad', index_col=0)

# Initialize sok_id column if it doesn't exist
if 'sok_id' not in soknad.columns:
    soknad['sok_id'] = pd.Series(range(1, len(soknad) + 1))

from openpyxl import load_workbook

def lagre_til_excel(data):
    filsti = r"C:\oblig5\is114-tema05\barnehage\kgdata.xlsx"
    
    # Prøv å laste inn eksisterende arbeidsbok, ellers opprett en ny
    try:
        workbook = load_workbook(filsti)
    except FileNotFoundError:
        workbook = None

    # Opprett dataframes for hver kategori
    foresatt_df = pd.DataFrame([{
        "Navn Foresatt": data.get("navn_foresatt"),
        "Adresse Foresatt": data.get("adresse_foresatt"),
        "Telefon Foresatt": data.get("telefon_foresatt"),
        "Personnummer Foresatt": data.get("personnummer_foresatt")
    }])
    
    barn_df = pd.DataFrame([{
        "Personnummer Barn": data.get("personnummer_barn"),
        "Fortrinnsrett Barnevern": data.get("fortrinnsrett_barnevern"),
        "Fortrinnsrett Sykdom i Familie": data.get("fortrinnsrett_sykdom_familie"),
        "Fortrinnsrett Sykdom på Barnet": data.get("fortrinnsrett_sykdom_barn"),
        "Fortrinnsrett Annet": data.get("fortrinnsrett_annet")
    }])
    
    soknad_df = pd.DataFrame([{
        "sok_id": len(soknad) + 1 if not soknad.empty else 1,
        "Liste over Barnehager": data.get("liste_over_barnehager"),
        "Tidspunkt for Oppstart": data.get("oppstart_tidspunkt"),
        "Har Søsken i Barnehagen": data.get("har_sosken_i_barnehagen"),
        "Brutto Inntekt Husholdning": data.get("brutto_inntekt")
    }])

    # Lagre til Excel
    with pd.ExcelWriter(filsti, engine="openpyxl", mode="a" if workbook else "w") as writer:
        foresatt_df.to_excel(writer, sheet_name="foresatt", index=False, header=not writer.sheets.get("foresatt"))
        barn_df.to_excel(writer, sheet_name="barn", index=False, header=not writer.sheets.get("barn"))
        soknad_df.to_excel(writer, sheet_name="soknad", index=False, header=not writer.sheets.get("soknad"))


def oppdater_data():
    global barnehage, forelder, barn, soknad
    kgdata = pd.ExcelFile(r'C:\oblig5\is114-tema05\barnehage\kgdata.xlsx')
    barnehage = pd.read_excel(kgdata, 'barnehage', index_col=0)
    forelder = pd.read_excel(kgdata, 'foresatt', index_col=0)
    barn = pd.read_excel(kgdata, 'barn', index_col=0)
    soknad = pd.read_excel(kgdata, 'soknad', index_col=0)

def commit_all():
    try:
        print("Skriver til Excel...")
        with pd.ExcelWriter(r'C:\oblig5\is114-tema05\barnehage\kgdata.xlsx', mode='w', engine='openpyxl') as writer:
            forelder.to_excel(writer, sheet_name='foresatt')
            barnehage.to_excel(writer, sheet_name='barnehage')
            barn.to_excel(writer, sheet_name='barn')
            soknad.to_excel(writer, sheet_name='soknad')
        print("Lagring fullført!")
    except Exception as e:
        print(f"Feil under lagring: {e}")

