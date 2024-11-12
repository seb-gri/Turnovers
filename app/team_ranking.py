# team_ranking.py
import streamlit as st
import pandas as pd
from .db import connect_db
from report_generator import generate_pdf_report  # Import de la fonction pour générer le PDF
import tempfile
import os
from datetime import datetime


def team_ranking():
    # Titre et sous-titres au centre de la page
    st.markdown("<h1 style='text-align: center;'>Classement par équipe des pertes techniques</h1>", unsafe_allow_html=True)
    
    competition_name = "Ligue 2 BKT"
    season = "Saison 2024/25"
    today_date = datetime.today().strftime("Au %d-%m-%Y")
    
    st.markdown(f"<h3 style='text-align: center;'>{competition_name} - {season}</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>{today_date}</h4>", unsafe_allow_html=True)
    
    # Connexion à la base de données et récupération des données
    conn = connect_db()
    query = '''
        SELECT team_name AS Equipe, COUNT(DISTINCT match_id) AS Matches_Joues,
               SUM(Miscontrol + Pass + Dribble + Shot) AS Total_Turnovers,
               SUM(Miscontrol) AS Miscontrol, SUM(Pass) AS Pass,
               SUM(Dribble) AS Dribble, SUM(Shot) AS Shot,
               (SUM(Miscontrol + Pass + Dribble + Shot) * 1.0 / COUNT(DISTINCT match_id)) AS Ratio_Turnovers_Match
        FROM turnovers
        GROUP BY team_name
        ORDER BY Ratio_Turnovers_Match ASC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Suppression des lignes vides
    df.dropna(how='all', inplace=True)

    # Ajout de la colonne de rang
    df.insert(0, 'Rang', range(1, len(df) + 1))

    # Formatage des colonnes
    df['Matches_Joues'] = df['Matches_Joues'].astype(int)
    df['Total_Turnovers'] = df['Total_Turnovers'].astype(int)
    df['Miscontrol'] = df['Miscontrol'].astype(int)
    df['Pass'] = df['Pass'].astype(int)
    df['Dribble'] = df['Dribble'].astype(int)
    df['Shot'] = df['Shot'].astype(int)
    df['Ratio_Turnovers_Match'] = df['Ratio_Turnovers_Match'].round(1)

    # Renommage des colonnes
    df = df.rename(columns={
        'Equipe': 'team',
        'Matches_Joues': 'matches_played',
        'Total_Turnovers': 'turnovers'
    })

    # Génération du nom du fichier PDF
    pdf_filename = f"Turnovers_equipe_{today_date}.pdf"

    # Affichage du DataFrame avec possibilité de tri
    df_display = df.set_index("Rang")
    st.dataframe(df_display, height=800)

    # Bouton pour générer le PDF
    if st.button("Générer le PDF du Classement"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            generate_pdf_report(df, tmp_pdf.name)

            # Téléchargement du fichier PDF
            with open(tmp_pdf.name, "rb") as pdf_file:
                st.download_button(
                    label="Télécharger le PDF",
                    data=pdf_file,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )

        # Suppression du fichier temporaire
        os.remove(tmp_pdf.name)
