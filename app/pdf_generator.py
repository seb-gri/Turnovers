from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, LongTable, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import tempfile
from datetime import datetime

def generate_pdf(dataframe, title, output_filename="Classement.pdf"):
    # Créer un fichier PDF temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf_path = tmp_pdf.name
        # Création du document PDF
        doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)

        # Styles et préparation des données
        styles = getSampleStyleSheet()
        body_text_style = styles['BodyText']
        body_text_style.fontSize = 6  # Taille de la police réduite pour compacter les informations
        body_text_style.leading = 7

        # Titre du PDF
        elements = [Paragraph(title, styles['Title'])]

        # Préparer les en-têtes de colonne et les données du tableau
        data = [[Paragraph(str(cell), body_text_style) for cell in dataframe.columns]]  # En-têtes de colonne

        # Remplir les lignes du tableau
        for row in dataframe.itertuples(index=False):
            row_data = []
            for cell in row:
                cell_text = str(cell)
                row_data.append(Paragraph(cell_text, body_text_style))
            data.append(row_data)

        # Ajustement automatique des largeurs de colonnes
        column_widths = [
            max(len(str(cell)) for cell in dataframe[column]) * 0.2 * cm
            for column in dataframe.columns
        ]
        max_page_width = A4[0] - doc.leftMargin - doc.rightMargin
        total_width = sum(column_widths)

        # Ajustement pour éviter de dépasser la largeur de la page
        if total_width > max_page_width:
            scale_factor = max_page_width / total_width
            column_widths = [width * scale_factor for width in column_widths]

        # Création du LongTable avec les données et les largeurs calculées
        table = LongTable(data, colWidths=column_widths)

        # Application des styles au tableau
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))

        # Ajouter le tableau au document
        elements.append(table)
        doc.build(elements)

    return pdf_path
