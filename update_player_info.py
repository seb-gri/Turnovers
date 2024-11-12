import sqlite3
from statsbombpy import sb
import logging

logging.basicConfig(filename='player_season_stats_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

def update_player_season_stats(db_name, competition_id, season_id):
    """
    Récupère les informations des joueurs de Ligue 2 à partir de l'API player_season_stats, puis met à jour la table 'player_info'.
    """
    try:
        # Récupérer les données des joueurs de la saison et compétition données
        player_stats = sb.player_season_stats(competition_id=competition_id, season_id=season_id)

        # Connexion à la base de données
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        for _, player in player_stats.iterrows():
            player_id = player['player_id']
            player_name = player['player_name']
            team_name = player['team_name']
            primary_position = player.get('primary_position', 'Unknown')

            # Vérifier si le joueur est déjà dans la table
            cursor.execute('SELECT primary_position FROM player_info WHERE player_id = ?', (player_id,))
            result = cursor.fetchone()

            if result is None:
                # Si le joueur n'est pas présent, l'ajouter
                cursor.execute('''INSERT INTO player_info (player_id, player_name, team_name, primary_position)
                                  VALUES (?, ?, ?, ?)''',
                               (player_id, player_name, team_name, primary_position))
                logging.info(f"Added new player: {player_name} (ID: {player_id})")
            elif result[0] != primary_position:
                # Si le joueur est présent mais que le poste principal a changé, le mettre à jour
                cursor.execute('''UPDATE player_info SET primary_position = ? WHERE player_id = ?''',
                               (primary_position, player_id))
                logging.info(f"Updated primary position for player: {player_name} (ID: {player_id})")

        # Sauvegarder les modifications
        conn.commit()
        conn.close()
        logging.info("Finished updating player info table.")
    except Exception as e:
        logging.error(f"Failed to update player info: {str(e)}")

if __name__ == "__main__":
    db_name = "turnovers.db"
    competition_id = 8  # Ligue 2
    season_id = 317  # Saison actuelle
    update_player_season_stats(db_name, competition_id, season_id)
