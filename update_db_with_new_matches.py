import sqlite3
from statsbombpy import sb

def update_db_with_new_matches(db_name, competition_id, season_id):
    """
    Met à jour la base de données avec les nouveaux matchs joués, les turnovers associés et le temps de jeu des joueurs.
    """
    matches = sb.matches(competition_id=competition_id, season_id=season_id)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    total_inserted_turnovers = 0  # Compteur pour les turnovers insérés

    for index, match in matches.iterrows():
        match_id = match['match_id']
        home_team = match['home_team']
        away_team = match['away_team']
        match_week = match.get('match_week', None)
        match_name = f"{home_team} vs {away_team}"
        
        cursor.execute("SELECT match_id FROM matches WHERE match_id = ?", (match_id,))
        if cursor.fetchone() is None:
            # Récupérer les événements du match
            try:
                events = sb.events(match_id=match_id)
                if events.empty:
                    continue  # Si aucun événement, passer au match suivant
            except ValueError:
                continue

            # Insérer le match dans la base de données
            cursor.execute('''INSERT INTO matches (match_id, match_date, home_team, away_team, competition_id, season_id, match_week)
                              VALUES (?, ?, ?, ?, ?, ?, ?)''',
                           (match_id, match['match_date'], home_team, away_team,
                            competition_id, season_id, match_week))

            # Initialiser les compteurs de turnovers pour chaque équipe
            turnovers = {
                home_team: {'Miscontrol': 0, 'Pass': 0, 'Dribble': 0, 'Shot': 0},
                away_team: {'Miscontrol': 0, 'Pass': 0, 'Dribble': 0, 'Shot': 0}
            }

            player_turnovers = {}  # Initialiser les compteurs de turnovers pour chaque joueur

            # Parcourir les événements pour identifier les turnovers et le temps de jeu
            for _, event in events.iterrows():
                team_name = event.get('team', None)
                player_id = event.get('player_id', None)
                player_name = event.get('player', None)
                position = event.get('position', None)
                period = event.get('period', None)
                minute = event.get('minute', None)
                second = event.get('second', None)
                location = event.get('location', None)
                event_type = event.get('type', None)
                event_id = event.get('id', None)

                if not team_name or not event_type:
                    continue

                # Initialiser le joueur dans le dictionnaire si nécessaire
                if player_id and event_id and event_id not in player_turnovers:
                    player_turnovers[event_id] = {'player_id': player_id, 'team_name': team_name, 'player': player_name, 'position': position, 'period': period, 'minute': minute, 'second': second, 'location': str(location), 'Miscontrol': 0, 'Pass': 0, 'Dribble': 0, 'Shot': 0}

                # Condition pour turnover : Miscontrol (Outcome n'est pas nécessaire)
                if event_type == 'Miscontrol':
                    turnovers[team_name]['Miscontrol'] += 1
                    if player_id and event_id:
                        player_turnovers[event_id]['Miscontrol'] += 1

                # Condition pour turnover : Pass avec pass_outcome "Incomplete" ou "Out"
                elif event_type == 'Pass':
                    pass_outcome = event.get('pass_outcome', None)
                    if pass_outcome in ['Incomplete', 'Out']:
                        turnovers[team_name]['Pass'] += 1
                        if player_id and event_id:
                            player_turnovers[event_id]['Pass'] += 1

                # Condition pour turnover : Dribble avec dribble_outcome "Incomplete"
                elif event_type == 'Dribble':
                    dribble_outcome = event.get('dribble_outcome', None)
                    if dribble_outcome == 'Incomplete':
                        turnovers[team_name]['Dribble'] += 1
                        if player_id and event_id:
                            player_turnovers[event_id]['Dribble'] += 1

                # Condition pour turnover : Shot avec shot_outcome "Off T", "Wayward", ou "Saved Off T"
                elif event_type == 'Shot':
                    shot_outcome = event.get('shot_outcome', None)
                    if shot_outcome in ['Off T', 'Wayward', 'Saved Off T']:
                        turnovers[team_name]['Shot'] += 1
                        if player_id and event_id:
                            player_turnovers[event_id]['Shot'] += 1

            # Insérer les turnovers par équipe dans la base de données
            for team, turnover_counts in turnovers.items():
                cursor.execute('''INSERT INTO turnovers (team_name, match_id, Miscontrol, Pass, Dribble, Shot)
                                  VALUES (?, ?, ?, ?, ?, ?)''',
                               (team, match_id, turnover_counts['Miscontrol'], turnover_counts['Pass'],
                                turnover_counts['Dribble'], turnover_counts['Shot']))
                total_inserted_turnovers += 1

            # Insérer les turnovers par joueur dans la base de données
            for event_id, turnover_counts in player_turnovers.items():
                if any([turnover_counts['Miscontrol'], turnover_counts['Pass'], turnover_counts['Dribble'], turnover_counts['Shot']]):
                    cursor.execute('''INSERT INTO player_turnovers (event_id, player_id, team_name, match_id, player, position, period, minute, second, location, Miscontrol, Pass, Dribble, Shot)
                                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                   (event_id, turnover_counts['player_id'], turnover_counts['team_name'], match_id, turnover_counts['player'], turnover_counts['position'],
                                    turnover_counts['period'], turnover_counts['minute'], turnover_counts['second'], turnover_counts['location'],
                                    turnover_counts['Miscontrol'], turnover_counts['Pass'], turnover_counts['Dribble'], turnover_counts['Shot']))

    conn.commit()
    conn.close()

    if total_inserted_turnovers == 0:
        print("Aucun turnover n'a été enregistré dans la base de données pour les nouveaux matchs.")
    else:
        print(f"{total_inserted_turnovers} enregistrements de turnovers ont été enregistrés.")