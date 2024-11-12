from statsbombpy import sb
import sqlite3
import pandas as pd

def get_played_matches(competition_id, season_id):
    """
    Récupère les matchs joués d'une compétition et d'une saison spécifiques.

    Parameters:
        competition_id (int): ID de la compétition.
        season_id (int): ID de la saison.

    Returns:
        pandas.DataFrame: DataFrame contenant uniquement les matchs qui ont été joués.
    """
    matches = sb.matches(competition_id=competition_id, season_id=season_id)

    # Filtrer pour ne garder que les matchs joués (utilisation de 'play_status' ou d'une autre clé pertinente)
    played_matches = matches[matches['play_status'] == 'Played']
    
    return played_matches

def process_played_matches(db_name, competition_id, season_id):
    """
    Traite uniquement les matchs joués d'une compétition et d'une saison spécifiques.
    
    Parameters:
        db_name (str): Nom de la base de données.
        competition_id (int): ID de la compétition.
        season_id (int): ID de la saison.
    """
    played_matches = get_played_matches(competition_id, season_id)

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Itération sur les matchs joués
    for index, match in played_matches.iterrows():
        match_id = match['match_id']
        try:
            print(f"Traitement du match joué ID {match_id}...")
            events = sb.events(match_id=match_id)
            
            # Calcul des turnovers et traitement des événements
            turnover_count = events[events['type']['name'] == 'Turnover'].shape[0]
            home_team = match['home_team']['name']
            away_team = match['away_team']['name']

            # Ajouter les données dans la base de données
            cursor.execute(
                """
                INSERT OR IGNORE INTO turnovers (match_id, home_team, away_team, turnovers)
                VALUES (?, ?, ?, ?)
                """,
                (match_id, home_team, away_team, turnover_count)
            )
            conn.commit()

        except Exception as e:
            print(f"Erreur lors du traitement du match ID {match_id}: {e}")

    conn.close()

def calculate_team_turnover_ratios(db_name):
    """
    Calcule le ratio de turnovers par match pour chaque équipe et retourne un DataFrame.
    """
    conn = sqlite3.connect(db_name)
    
    query = '''
        SELECT team_name AS team, 
               COUNT(DISTINCT match_id) AS matches_played,
               SUM(Miscontrol) AS Miscontrol, 
               SUM(Pass) AS Pass, 
               SUM(Dribble) AS Dribble, 
               SUM(Shot) AS Shot,
               SUM(Miscontrol) + SUM(Pass) + SUM(Dribble) + SUM(Shot) AS total_turnovers
        FROM turnovers
        GROUP BY team_name
        ORDER BY team_name
    '''
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Calculer le ratio turnovers par match
    df['Ratio_Turnovers_Match'] = (df['total_turnovers'] / df['matches_played']).round(1)
    
    # Ajouter une colonne de classement (Rang) basée sur le ratio turnovers/match
    df['Rang'] = df['Ratio_Turnovers_Match'].rank(method='dense', ascending=True).astype(int)

    # Réorganiser l'ordre des colonnes pour inclure Rang et Ratio_Turnovers_Match
    df = df[['Rang', 'team', 'matches_played', 'Miscontrol', 'Pass', 'Dribble', 'Shot', 'total_turnovers', 'Ratio_Turnovers_Match']]
    
    return df