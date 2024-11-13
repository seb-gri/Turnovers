# main.py
from statsbombpy import sb
from report_generator import generate_pdf_report
from datetime import datetime
from initialize_db import initialize_db
from update_db_with_new_matches import update_db_with_new_matches
from update_player_playtime import update_player_playtime
from update_player_info import update_player_season_stats
from update_player_passes import fetch_and_insert_player_passes
from utils import convert_timestamp_to_seconds
import sqlite3
from data_processing import calculate_team_turnover_ratios
import config  # Importer les paramètres depuis config.py

def main():
    db_name = config.DB_NAME
    competition_id = config.COMPETITION_ID
    season_id = config.SEASON_ID

    # Initialiser la base de données si nécessaire
    initialize_db(db_name)

    # Mettre à jour les informations des joueurs
    update_player_season_stats(db_name, competition_id, season_id)

    # Mettre à jour la base de données avec les nouveaux matchs joués
    update_db_with_new_matches(db_name, competition_id, season_id)

    # Mettre à jour la base de données avec les relances des joueurs initiées dans leur camp
    fetch_and_insert_player_passes(db_name, competition_id, season_id)

    # Récupérer tous les matchs déjà insérés dans la base pour mettre à jour le temps de jeu des joueurs
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT match_id FROM matches")
    matches = cursor.fetchall()
    conn.close()

    # Mettre à jour le temps de jeu des joueurs pour chaque match
    for match in matches:
        match_id = match[0]
        update_player_playtime(db_name, match_id)

    # Calculer les ratios turnovers/matchs par équipe
    team_stats = calculate_team_turnover_ratios(db_name)

    # Générer le classement au format PDF
    # today = datetime.today().strftime('%Y-%m-%d')
    # output_file = f"classement_turnovers_{today}.pdf"
    # generate_pdf_report(team_stats, output_file)
    # print(f"Rapport PDF généré: {output_file}")

if __name__ == "__main__":
    main()
