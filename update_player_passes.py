import sqlite3
from statsbombpy import sb

def fetch_and_insert_player_passes(db_name, competition_id, season_id):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Récupérer les matchs pour la compétition et la saison spécifiées
    matches = sb.matches(competition_id, season_id)
    match_ids = matches['match_id'].tolist()
    
    for match_id in match_ids:
        try:
            events = sb.events(match_id)
        except ValueError as e:
            print(f"Erreur lors de la récupération des événements pour le match ID {match_id}: {e}")
            continue  # Passer au match suivant en cas d'erreur

        # Vérifier que `events` contient des données avant de traiter
        if events.empty:
            print(f"Aucun événement disponible pour le match ID {match_id}.")
            continue  # Passer au match suivant s'il n'y a pas d'événements

        # Filtrer pour les passes depuis leur propre camp
        passes = events[
            (events['type'] == 'Pass') &
            (events['location'].apply(lambda loc: isinstance(loc, list) and loc[0] < 60))  # Vérifie que 'location' est une liste avant d'accéder à loc[0]
        ]

        # Insérer chaque passe dans la table relances_joueur
        for _, pass_event in passes.iterrows():
            pass_id = pass_event['id']
            player_id = pass_event['player_id']
            player_name = pass_event['player']
            team_name = pass_event['team']
            match_teams = f"{matches.loc[matches['match_id'] == match_id, 'home_team'].values[0]} vs {matches.loc[matches['match_id'] == match_id, 'away_team'].values[0]}"
            match_date = matches.loc[matches['match_id'] == match_id, 'match_date'].values[0]
            pass_result = pass_event.get('pass_outcome')
            recipient_name = pass_event.get('pass_recipient')
            start_x = pass_event['location'][0] if isinstance(pass_event['location'], list) else None
            start_y = pass_event['location'][1] if isinstance(pass_event['location'], list) else None
            end_x = pass_event['pass_end_location'][0] if isinstance(pass_event['pass_end_location'], list) else None
            end_y = pass_event['pass_end_location'][1] if isinstance(pass_event['pass_end_location'], list) else None
            under_pressure = 1 if pass_event.get('under_pressure') else 0

            cursor.execute('''
                INSERT OR IGNORE INTO relances_joueur (
                    pass_id, player_id, player_name, team_name, match_id, match_teams, match_date,
                    pass_result, recipient_name, start_x, start_y, end_x, end_y, under_pressure
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (pass_id, player_id, player_name, team_name, match_id, match_teams, match_date,
                  pass_result, recipient_name, start_x, start_y, end_x, end_y, under_pressure))

    conn.commit()
    conn.close()
