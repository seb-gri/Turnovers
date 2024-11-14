import sqlite3
import time
from datetime import datetime
from statsbombpy import sb
from report_generator import generate_pdf_report
from initialize_db import initialize_db
from update_db_with_new_matches import update_db_with_new_matches
from update_player_playtime import update_player_playtime
from update_player_info import update_player_season_stats
from update_player_passes import fetch_and_insert_player_passes
from data_processing import calculate_team_turnover_ratios
import config  # Importer les paramètres depuis config.py

# Décorateur pour mesurer le temps d'exécution de chaque fonction
def timer(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        duration = end_time - start_time
        print(f"Temps d'exécution de {func.__name__}: {duration:.2f} secondes")
        return result
    return wrapper

@timer
def initialize_database(db_name):
    initialize_db(db_name)

@timer
def update_player_statistics(db_name, competition_id, season_id):
    update_player_season_stats(db_name, competition_id, season_id)

@timer
def update_matches_database(db_name, competition_id, season_id):
    update_db_with_new_matches(db_name, competition_id, season_id)

@timer
def insert_player_passes(db_name, competition_id, season_id):
    fetch_and_insert_player_passes(db_name, competition_id, season_id)

@timer
def update_playtime_for_matches(db_name, matches):
    for match in matches:
        match_id = match[0]
        update_player_playtime(db_name, match_id)

@timer
def calculate_team_stats(db_name):
    return calculate_team_turnover_ratios(db_name)

# Fonction principale avec chronométrage des étapes
def main():
    db_name = config.DB_NAME
    competition_id = config.COMPETITION_ID
    season_id = config.SEASON_ID

    # Initialiser la base de données si nécessaire
    initialize_database(db_name)

    # Mettre à jour les informations des joueurs
    update_player_statistics(db_name, competition_id, season_id)

    # Mettre à jour la base de données avec les nouveaux matchs joués
    update_matches_database(db_name, competition_id, season_id)

    # Mettre à jour la base de données avec les relances des joueurs initiées dans leur camp
    insert_player_passes(db_name, competition_id, season_id)

    # Récupérer tous les matchs déjà insérés dans la base pour mettre à jour le temps de jeu des joueurs
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT match_id FROM matches")
    matches = cursor.fetchall()
    conn.close()

    # Mettre à jour le temps de jeu des joueurs pour chaque match
    update_playtime_for_matches(db_name, matches)

    # Calculer les ratios turnovers/matchs par équipe
    team_stats = calculate_team_stats(db_name)

    # Générer le classement au format PDF
    # today = datetime.today().strftime('%Y-%m-%d')
    # output_file = f"classement_turnovers_{today}.pdf"
    # generate_pdf_report(team_stats, output_file)
    # print(f"Rapport PDF généré: {output_file}")

if __name__ == "__main__":
    main()
