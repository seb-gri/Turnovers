# run_app.py
import streamlit as st

# Configuration de la page (doit être la première commande Streamlit exécutée)
st.set_page_config(page_title="Tableau de bord Clermont Foot 63", layout="wide")

# Importations après la configuration de la page
from app.main_page import home
from app.team_ranking import team_ranking
from app.player_ranking import player_ranking
from app.relances.relances import relances_page

# Titre principal du projet
st.title("Tableau de bord Clermont Foot 63")

# Menu principal dans la barre latérale pour choisir la section
main_menu = st.sidebar.radio("Menu principal", ["Accueil", "Pertes techniques", "Relances"])

# Affichage de la navigation et du contenu en fonction du menu sélectionné
if main_menu == "Accueil":
    # Page d'accueil principale
    home()

elif main_menu == "Pertes techniques":
    # Navigation spécifique à "Pertes techniques"
    st.sidebar.title("Navigation - Pertes techniques")
    page = st.sidebar.radio("Aller à", ("Classement par Équipe", "Classement par Joueur"))

    # Affichage de la page sélectionnée dans "Pertes techniques"
    if page == "Classement par Équipe":
        team_ranking()
    elif page == "Classement par Joueur":
        player_ranking()

elif main_menu == "Relances":
    # Navigation spécifique à "Relances"
    st.sidebar.title("Navigation - Relances")
    relances_page_selection = st.sidebar.radio("Aller à", ("Accueil", "Statistiques Relances", "Analyse Avancée"))

    # Affichage de la page sélectionnée dans "Relances"
    if relances_page_selection == "Accueil":
        relances_page()
    elif relances_page_selection == "Statistiques Relances":
        st.write("Statistiques des Relances")
    elif relances_page_selection == "Analyse Avancée":
        st.write("Analyse Avancée des Relances")