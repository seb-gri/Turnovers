import streamlit as st
import pandas as pd
from .db import connect_db
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
import tempfile
import os
from datetime import datetime
from math import floor

def add_page_number(canvas, doc):
    page_num = canvas.getPageNumber()
    total_pages = doc.page_count
    canvas.drawRightString(200 * mm, 10 * mm, f"Page {page_num}/{total_pages}")

def player_ranking():
    st.markdown("# Classement par Joueur", unsafe_allow_html=True)
    conn = connect_db()
    
    # Récupérer les turnovers des joueurs
    turnovers_query = '''
        SELECT player_id, player AS Joueur, player_turnovers.team_name AS Equipe,
               SUM(Miscontrol) AS Miscontrol, SUM(Pass) AS Pass, SUM(Dribble) AS Dribble,
               SUM(Shot) AS Shot, SUM(Miscontrol + Pass + Dribble + Shot) AS Turnovers
        FROM player_turnovers
        GROUP BY player_id, player, player_turnovers.team_name
    '''
    turnovers_df = pd.read_sql(turnovers_query, conn)
    
    # Récupérer les minutes jouées des joueurs
    playtime_query = '''
        SELECT player_id, SUM(playtime) AS Minutes
        FROM player_playtime
        GROUP BY player_id
    '''
    playtime_df = pd.read_sql(playtime_query, conn)
    
    # Récupérer les postes des joueurs
    position_query = '''
        SELECT player_id, primary_position AS Poste
        FROM player_info
    '''
    position_df = pd.read_sql(position_query, conn)
    conn.close()

    # Convertir les noms de postes en initiales en gérant les valeurs nulles
    position_df['Poste'] = position_df['Poste'].apply(lambda x: ''.join(word[0].upper() for word in x.split()) if isinstance(x, str) else x)

    # Fusionner les trois DataFrames sur l'identifiant du joueur
    df = pd.merge(turnovers_df, playtime_df, on='player_id', how='left')
    df = pd.merge(df, position_df, on='player_id', how='left')

    # Arrondir les minutes à l'entier inférieur
    df['Minutes'] = df['Minutes'].apply(lambda x: floor(x) if pd.notna(x) else 0)

    # Calculer le ratio turnovers par 90 minutes
    df['Ratio'] = ((df['Turnovers'] * 90.0) / df['Minutes']).round(1)
    df.drop(columns=['player_id'], inplace=True)

    # Réorganiser l'ordre des colonnes
    df = df[['Joueur', 'Equipe', 'Poste', 'Minutes', 'Miscontrol', 'Pass', 'Dribble', 'Shot', 'Turnovers', 'Ratio']]

    # Appliquer les filtres
    max_minutes = int(df['Minutes'].max())
    default_value = min(max_minutes // 2, 1200)
    min_minutes = st.slider('Filtrer les joueurs par minutes jouées (minimum)', min_value=0, max_value=max_minutes, value=default_value)
    df_filtered = df[df['Minutes'] >= min_minutes]

    # Filtre par équipe
    equipes = st.multiselect('Filtrer par équipe(s)', options=sorted(df['Equipe'].dropna().unique()), default=sorted(df['Equipe'].dropna().unique()))
    if equipes:
        df_filtered = df_filtered[df_filtered['Equipe'].isin(equipes)]

    # Filtre par poste
    postes = st.multiselect('Filtrer par poste(s)', options=df['Poste'].dropna().unique(), default=df['Poste'].dropna().unique())
    if postes:
        df_filtered = df_filtered[df_filtered['Poste'].isin(postes)]

    # Supprimer les lignes qui contiennent des valeurs NaN
    df_filtered.dropna(how='all', inplace=True)

    # Commencer la numérotation des lignes à 1
    df_filtered.index += 1

    # Afficher le tableau avec tri par colonne et sans scroll
    st.dataframe(df_filtered, height=35 * len(df_filtered))

    # Bouton pour générer le PDF
    if st.button("Générer le PDF du Classement"):
        # Enregistrer le PDF temporairement
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            pdf_path = tmp_pdf.name

            # Création du document PDF avec marges de 1 cm
            doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=1 * cm, leftMargin=1 * cm, topMargin=1 * cm, bottomMargin=1 * cm)

            # Styles et données du tableau
            styles = getSampleStyleSheet()
            title_style = styles['Title']
            title_style.fontSize = 14  # Taille de police pour le titre
            title_style.alignment = 1  # Centre le titre
            body_text_style = styles['BodyText']
            body_text_style.fontSize = 8  # Augmenter la taille de la police
            body_text_style.leading = 10  # Augmenter l'espacement des lignes

            # Titre du PDF
            title = Paragraph("Classement des Pertes Techniques par joueur", title_style)

            # En-têtes de colonne et données
            data = [[Paragraph(str(cell), body_text_style) for cell in df_filtered.columns]]  # En-têtes de colonne
            for row in df_filtered.itertuples(index=False):
                row_data = [Paragraph(str(cell), body_text_style) for cell in row]
                data.append(row_data)

            # Ajustement des largeurs de colonnes pour ne pas dépasser les marges
            column_widths = [
                min(max(len(str(df_filtered[column].astype(str).max())) * 0.2 * cm, 2 * cm), 5 * cm)  # Min 2 cm, max 5 cm par colonne
                for column in df_filtered.columns
            ]

            # Créer le tableau avec ReportLab
            table = Table(data, colWidths=column_widths)

            # Appliquer les styles du tableau pour centrer le contenu
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Centrage du contenu
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),  # Taille de police augmentée
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))

            # Construction du document
            elements = [title, table]
            doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)

            # Téléchargement du PDF
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="Télécharger le PDF",
                    data=pdf_file,
                    file_name=f"Classement_Joueur_{datetime.today().strftime('%Y-%m-%d')}.pdf",
                    mime="application/pdf"
                )

            # Supprimer le fichier temporaire après le téléchargement
            os.remove(pdf_path)
