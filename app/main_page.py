# main_page.py
import streamlit as st
import os
import pandas as pd
from app.utils.helpers import format_date  # Import de la fonction utilitaire pour formater la date
import sys
import subprocess

print("Python executable:", sys.executable)

def home():
    st.title("Accueil")
    st.write("Bienvenue sur la plateforme d'analyse des turnovers de Ligue 2 !")

    # Bouton pour mettre à jour les données
    if st.button("Mettre à jour les données"):
        # Exécution du script `main.py` pour mettre à jour les données
        result = subprocess.run([sys.executable, "main.py"], capture_output=True, text=True)
        
        # Vérification du succès de l'exécution
        if result.returncode == 0:
            # Enregistrement de la date et de l'heure de la mise à jour dans un fichier texte
            with open("last_update.txt", "w") as file:
                file.write(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))
            st.success("Les données ont été mises à jour avec succès.")
        else:
            st.error("Erreur lors de la mise à jour des données.")
            st.text(f"Erreur : {result.stderr}")  # Affiche le message d'erreur

    # Afficher la date de la dernière mise à jour
    if os.path.exists("last_update.txt"):
        with open("last_update.txt", "r") as file:
            last_update = file.read()
        
        # Formattage de la date avant affichage
        formatted_date = format_date(pd.to_datetime(last_update))
        st.write(f"Dernière mise à jour : {formatted_date}")
    else:
        st.write("Dernière mise à jour : Non disponible")
