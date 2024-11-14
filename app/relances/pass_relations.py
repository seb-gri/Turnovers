import streamlit as st
import pandas as pd
from ..db import connect_db  # Import de la fonction connect_db

def pass_relations():
    conn = connect_db()  # Connexion à la base de données

    st.title("Analyse des relations de passes")

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

    # Étape 1 : Calcul du temps de jeu total pour chaque joueur (passeur et receveur)
    query_playtime = """
        SELECT player_name, SUM(playtime) AS Temps_Jeu_Total
        FROM player_playtime
        GROUP BY player_name
    """
    playtime_data = pd.read_sql(query_playtime, conn)
    playtime_dict = playtime_data.set_index('player_name')['Temps_Jeu_Total'].to_dict()

    # Étape 2 : Requête principale pour les données de relations de passes
    query = """
        SELECT r.player_id AS passeur_id, r.player_name AS Passeur, p.primary_position AS Poste_P,
               r.recipient_name AS Receveur, pr.primary_position AS Poste_R,
               COUNT(*) AS Tot_Passes,
               SUM(CASE WHEN r.pass_result IS null THEN 1 ELSE 0 END) AS Tot_Passes_R
        FROM relances_joueur AS r
        LEFT JOIN player_info AS p ON r.player_id = p.player_id
        LEFT JOIN player_info AS pr ON r.recipient_name = pr.player_name
        WHERE r.team_name = ? AND r.start_x BETWEEN ? AND ?
        GROUP BY r.player_id, r.recipient_name, p.primary_position, pr.primary_position
    """
    
    params = (team, start_location, end_location)
    
    try:
        # Exécution de la requête SQL
        data = pd.read_sql(query, conn, params=params)

        # Ajout du temps de jeu total pour chaque joueur
        data['Temps_Jeu_Passeur'] = data['Passeur'].map(playtime_dict).fillna(0)
        data['Temps_Jeu_Receveur'] = data['Receveur'].map(playtime_dict).fillna(0)

        # Filtrage en fonction du temps de jeu sélectionné
        data = data[(data['Temps_Jeu_Passeur'] >= min_playtime) & (data['Temps_Jeu_Passeur'] <= max_playtime) &
                    (data['Temps_Jeu_Receveur'] >= min_playtime) & (data['Temps_Jeu_Receveur'] <= max_playtime)]

        # Calcul du temps de jeu en commun et des colonnes demandées
        data['Tps jeu X'] = data[['Temps_Jeu_Passeur', 'Temps_Jeu_Receveur']].min(axis=1).astype(int)
        data['Moy.Passes'] = data.apply(lambda row: round(row['Tot_Passes'] * 90 / row['Tps jeu X'], 2) if row['Tps jeu X'] > 0 else None, axis=1)
        
        # Calcul du ratio de passes réussies
        data['Ratio Passes'] = data.apply(lambda row: f"{int((row['Tot_Passes_R'] / row['Tot_Passes']) * 100)}%" 
                                          if row['Tot_Passes'] > 0 else None, axis=1)

        # Tri du tableau par Moy.Passes en ordre décroissant
        data = data.sort_values(by='Moy.Passes', ascending=False)

        # Suppression des colonnes intermédiaires inutiles pour l'affichage
        data = data.drop(columns=['passeur_id', 'Temps_Jeu_Passeur', 'Temps_Jeu_Receveur', 'Tot_Passes', 'Tot_Passes_R'])

    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête SQL : {e}")
        conn.close()
        return

    conn.close()

    # Affichage des données filtrées et triées dans Streamlit en utilisant toute la largeur
    st.dataframe(data, use_container_width=True)
