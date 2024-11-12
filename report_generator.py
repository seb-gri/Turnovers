# report_generator.py
from fpdf import FPDF
from datetime import datetime

def generate_pdf_report(dataframe, output_file):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=12)
    
    # Titre principal
    pdf.cell(0, 10, "Classement par équipe des pertes techniques", ln=True, align="C")
     
    # Informations sur la compétition, la saison et la date du jour
    competition_name = "Ligue 2"  # Remplacez par le nom exact de la compétition concernée
    season = "Saison 2024/25"  # Remplacez par la saison actuelle
    today_date = datetime.today().strftime("Au %d-%m-%Y")
    
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 8, f"{competition_name} - {season}", ln=True, align="C")
    pdf.cell(0, 8, today_date, ln=True, align="C")
    pdf.ln(10)  # Espace entre le titre et le tableau

    # Largeurs des colonnes ajustées pour chaque en-tête
    column_widths = [14, 30, 20, 20, 20, 20, 20, 20, 20]
    row_height = 8

    # Création des en-têtes du tableau
    headers = ["Rang", "Équipe", "Matches", "Miscontrol", "Pass", "Dribble", "Shot", "Turnovers", "Ratio T/M"]
    for i, header in enumerate(headers):
        pdf.cell(column_widths[i], row_height, header, border=1, align="C")
    pdf.ln(row_height)

    # Remplissage des lignes du tableau
    for _, row in dataframe.iterrows():
        pdf.cell(column_widths[0], row_height, str(row['Rang']), border=1, align="C")
        pdf.cell(column_widths[1], row_height, row['team'], border=1, align="C")
        pdf.cell(column_widths[2], row_height, str(row['matches_played']), border=1, align="C")
        pdf.cell(column_widths[4], row_height, str(row['Miscontrol']), border=1, align="C")
        pdf.cell(column_widths[5], row_height, str(row['Pass']), border=1, align="C")
        pdf.cell(column_widths[6], row_height, str(row['Dribble']), border=1, align="C")
        pdf.cell(column_widths[7], row_height, str(row['Shot']), border=1, align="C")
        pdf.cell(column_widths[3], row_height, str(row['turnovers']), border=1, align="C")
        pdf.cell(column_widths[8], row_height, f"{row['Ratio_Turnovers_Match']:.1f}", border=1, align="C")
        pdf.ln(row_height)

    pdf.output(output_file)
