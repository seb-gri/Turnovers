from fpdf import FPDF

def generate_pdf_report(team_stats, output_file):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Classement des équipes par ratio turnovers/match", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    
    # Ajouter les en-têtes de colonnes pour le tableau
    headers = ["Équipe", "Matches joués", "Miscontrol", "Pass", "Dribble", "Shot", "Total Turnovers", "Ratio"]
    for header in headers:
        pdf.cell(25, 10, header, border=1, align='C')
    pdf.ln()

    # Ajouter les statistiques de chaque équipe dans le tableau
    for _, row in team_stats.iterrows():
        team_name = row['team']
        matches_played = row['matches_played']
        miscontrol = row['Miscontrol']
        pass_turnovers = row['Pass']
        dribble = row['Dribble']
        shot = row['Shot']
        total_turnovers = miscontrol + pass_turnovers + dribble + shot
        ratio = total_turnovers / matches_played if matches_played > 0 else 0

        pdf.cell(25, 10, team_name, border=1, align='C')
        pdf.cell(25, 10, str(matches_played), border=1, align='C')
        pdf.cell(25, 10, str(miscontrol), border=1, align='C')
        pdf.cell(25, 10, str(pass_turnovers), border=1, align='C')
        pdf.cell(25, 10, str(dribble), border=1, align='C')
        pdf.cell(25, 10, str(shot), border=1, align='C')
        pdf.cell(25, 10, str(total_turnovers), border=1, align='C')
        pdf.cell(25, 10, f"{ratio:.2f}", border=1, align='C')
        pdf.ln()

    pdf.output(output_file)
