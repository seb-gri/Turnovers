from statsbombpy import sb
from database import initialize_db, update_db_with_new_matches
from report_generator import generate_pdf_report
from datetime import datetime

from data_processing import calculate_team_turnover_ratios
import config  # Importer les paramètres depuis config.py

def main():
    db_name = config.DB_NAME
    competition_id = config.COMPETITION_ID
    season_id = config.SEASON_ID

    # Initialiser la base de données si nécessaire
    initialize_db(db_name)

    # Mettre à jour la base de données avec les nouveaux matchs joués
    update_db_with_new_matches(db_name, competition_id, season_id)

    # Calculer les ratios turnovers/matchs par équipe
    calculate_team_turnover_ratios(db_name)

    # Récupérer les ratios turnovers/match depuis la base de données
    team_stats = calculate_team_turnover_ratios(db_name)

    # Générer le classement au format PDF
    today = datetime.today().strftime('%Y-%m-%d')
    output_file = f"classement_turnovers_{today}.pdf"
    generate_pdf_report(team_stats, output_file)
    print(f"Rapport PDF généré: {output_file}")

if __name__ == "__main__":
    main()