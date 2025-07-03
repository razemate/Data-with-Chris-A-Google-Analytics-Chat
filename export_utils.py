import pandas as pd
from fpdf import FPDF
from docx import Document

def export_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def export_pdf(df, title):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    # Add table implementation here
    return pdf.output(dest='S').encode('latin1')
