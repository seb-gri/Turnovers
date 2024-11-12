import sqlite3
import pandas as pd
import logging
from statsbombpy import sb

logging.basicConfig(filename='player_playtime_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

def update_player_playtime(db_name, match_id):
    """
    Met à jour la table player_playtime avec le temps de jeu des joueurs pour un match spécifique en utilisant l'API Player Match Stats.
    """
    try:
        # Récupérer les statistiques des joueurs pour un match donné
        player_stats = sb.player_match_stats(match_id=match_id)
        
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Parcourir les statistiques des joueurs
        for _, player in player_stats.iterrows():
            player_id = player['player_id']
            player_name = player['player_name']
            team_name = player['team_name']
            playtime = player['player_match_minutes']
            match_name = f"{player['team_name']} vs {player_stats[player_stats['team_id'] != player['team_id']]['team_name'].unique()[0]}"

            # Insérer ou mettre à jour le temps de jeu dans la base de données
            cursor.execute('''INSERT OR REPLACE INTO player_playtime (player_id, match_id, team_name, player_name, match, playtime)
                              VALUES (?, ?, ?, ?, ?, ?)''',
                           (player_id, match_id, team_name, player_name, match_name, playtime))
        
        conn.commit()
        conn.close()
        logging.info(f"Finished updating player playtime for match ID: {match_id}")
    
    except Exception as e:
        logging.error(f"Failed to update player playtime for match ID {match_id}: {str(e)}")
