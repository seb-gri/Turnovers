import sqlite3
import pandas as pd
from statsbombpy import sb

def fetch_and_insert_player_passes(db_name, competition_id, season_id):
    # Démarrer le chronomètre
    
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Récupérer les matchs de la base de données
    cursor.execute('SELECT match_id, match_date, home_team, away_team FROM matches WHERE competition_id = ? AND season_id = ?', (competition_id, season_id))
    match_data = cursor.fetchall()

    for match_row in match_data:
        match_id, match_date, home_team, away_team = match_row

        # Récupérer les événements pour le match et trier par timestamp
        events = sb.events(match_id=match_id)
        events = events.sort_values(by='timestamp').reset_index(drop=True)

        # Vérifier si des événements ont été récupérés
        if events.empty:
            print(f"Aucun événement pour le match {match_id}")
            continue

        # Filtrer les passes
        passes = events[events['type'] == 'Pass'].copy()

        # Initialiser la colonne under_pressure à 0 par défaut
        passes['under_pressure'] = 0

        # Mettre à jour under_pressure en fonction de l'événement précédent
        for i, pass_event in passes.iterrows():
            event_index = pass_event.name
            if event_index > 0 and events.iloc[event_index - 1]['type'] == 'Pressure':
                passes.at[pass_event.name, 'under_pressure'] = 1

        # Insérer les données dans la base de données
        for _, row in passes.iterrows():
            player_id = row.get('player_id')
            player_name = row.get('player')
            team_name = row.get('team')
            # Vérifiez et définissez 'Complete' si pass_outcome est None ou absent
            pass_outcome = row.get('pass_outcome') if row.get('pass_outcome') else 'Complete'
            recipient_name = row.get('pass_recipient')
            start_x = row['location'][0] if isinstance(row.get('location'), list) else None
            start_y = row['location'][1] if isinstance(row.get('location'), list) else None
            end_x = row['pass_end_location'][0] if isinstance(row.get('pass_end_location'), list) else None
            end_y = row['pass_end_location'][1] if isinstance(row.get('pass_end_location'), list) else None

            cursor.execute('''
                INSERT OR REPLACE INTO relances_joueur (
                    pass_id, player_id, player_name, team_name, match_id, match_teams, match_date,
                    pass_result, recipient_name, start_x, start_y, end_x, end_y, under_pressure
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['id'],
                player_id,
                player_name,
                team_name,
                match_id,
                f"{home_team} vs {away_team}",
                match_date,
                pass_outcome,
                recipient_name,
                start_x,
                start_y,
                end_x,
                end_y,
                row['under_pressure']
            ))

    # Valider les modifications
    conn.commit()
    conn.close()
