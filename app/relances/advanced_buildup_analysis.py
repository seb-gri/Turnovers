import streamlit as st
import pandas as pd
from ..db import connect_db  # Import de la fonction connect_db

def advanced_buildup_analysis():
    conn = connect_db()  # Connexion à la base de données

    st.title("Analyse avancée des relances basses")

    # Filtrage par temps de jeu
    min_playtime, max_playtime = st.slider("Temps de jeu (en minutes)", 0, 5000, (0, 5000))

    # Récupération des noms d'équipes uniques pour le filtre d'équipe
    query_teams = "SELECT DISTINCT team_name FROM relances_joueur"
    teams = pd.read_sql(query_teams, conn)['team_name'].tolist()
    
    # Tri des équipes par ordre alphabétique
    teams.sort()
    
    # Vérification et ajout de "Clermont Foot" dans la liste des équipes si absent, puis le définir par défaut
    if "Clermont Foot" not in teams:
        teams.insert(0, "Clermont Foot")
    default_team = "Clermont Foot" if "Clermont Foot" in teams else teams[0]
    
    # Filtrage par équipe
    team = st.selectbox("Sélectionnez l'équipe", teams, index=teams.index(default_team))
    
    # Filtrage par localisation de départ
    start_location = st.slider("Localisation de départ minimale (x)", 0.0, 105.0, 0.0)
    end_location = st.slider("Localisation de départ maximale (x)", 0.0, 105.0, 52.5)

    # Étape 1 : Calcul du temps de jeu total pour chaque joueur
    query_playtime = """
        SELECT player_id, SUM(playtime) AS Temps_Jeu_Total
        FROM player_playtime
        GROUP BY player_id
    """
    playtime_data = pd.read_sql(query_playtime, conn)
    playtime_dict = playtime_data.set_index('player_id')['Temps_Jeu_Total'].to_dict()

    # Étape 2 : Requête principale pour les données de relances
    query = """
        SELECT r.player_name AS Joueur, r.team_name AS Équipe, p.primary_position AS Poste,
               COUNT(*) AS Tot_Passes,
               SUM(CASE WHEN r.pass_result IS NULL THEN 1 ELSE 0 END) AS Tot_Passes_R,
               SUM(CASE WHEN r.under_pressure = 1 THEN 1 ELSE 0 END) AS Tot_Passes_ssP,
               SUM(CASE WHEN r.pass_result IS NULL AND r.under_pressure = 1 THEN 1 ELSE 0 END) AS Tot_Passes_R_ssP,
               r.player_id AS player_id
        FROM relances_joueur AS r
        LEFT JOIN player_info AS p ON r.player_id = p.player_id
        WHERE r.team_name = ? AND r.start_x BETWEEN ? AND ?
        GROUP BY r.player_name, r.team_name, p.primary_position, r.player_id
    """
    
    params = (team, start_location, end_location)
    
    try:
        # Exécution de la requête SQL
        data = pd.read_sql(query, conn, params=params)

        # Ajout du temps de jeu total pour calculs de moyennes
        data['Temps_Jeu_Total'] = data['player_id'].map(playtime_dict).fillna(0)  # Remplacer NaN par 0

        # Filtrage en fonction du temps de jeu sélectionné
        data = data[(data['Temps_Jeu_Total'] >= min_playtime) & (data['Temps_Jeu_Total'] <= max_playtime)]

        # Calcul des colonnes demandées
        data['Moy.Passes'] = data.apply(lambda row: round(row['Tot_Passes'] * 90 / row['Temps_Jeu_Total'], 2) if row['Temps_Jeu_Total'] > 0 else None, axis=1)
        data['Ratio Passes'] = data.apply(lambda row: round(row['Tot_Passes_R'] / row['Tot_Passes'] * 100, 2) if row['Tot_Passes'] > 0 else None, axis=1)
        data['Moy.Passes ssP'] = data.apply(lambda row: round(row['Tot_Passes_ssP'] * 90 / row['Temps_Jeu_Total'], 2) if row['Temps_Jeu_Total'] > 0 else None, axis=1)
        data['Ratio Passes ssP'] = data.apply(lambda row: round(row['Tot_Passes_R_ssP'] / row['Tot_Passes_ssP'] * 100, 2) if row['Tot_Passes_ssP'] > 0 else None, axis=1)

        # Calcul de la différence entre Ratio Passes ssP et Ratio Passes, en pourcentage entier
        data['Diff.Ratio'] = data.apply(lambda row: int(round(row['Ratio Passes ssP'] - row['Ratio Passes'])) if pd.notnull(row['Ratio Passes']) and pd.notnull(row['Ratio Passes ssP']) else None, axis=1)

        # Ajout de la colonne Temps de jeu (Tps jeu) en affichant uniquement la partie entière
        data['Tps jeu'] = data['Temps_Jeu_Total'].astype(int)

        # Suppression des colonnes intermédiaires inutiles pour l'affichage
        data = data.drop(columns=['player_id', 'Tot_Passes', 'Tot_Passes_R', 'Tot_Passes_ssP', 'Tot_Passes_R_ssP', 'Temps_Jeu_Total'])

    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête SQL : {e}")
        conn.close()
        return

    conn.close()

    # Affichage des données filtrées dans Streamlit
    st.write(data)
