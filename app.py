import streamlit as st
import fitz
from google import genai
from google.genai import types
from docx import Document
import io

# Konfiguracja
client = genai.Client(api_key=st.secrets["GEMINI_KEY"])

st.title("📚 Generator Notatek")

# Upload
pdf = st.file_uploader("Wrzuć PDF", type="pdf")

# Tryb
tryb = st.radio("Tryb:", ["Skrót", "Zwykły", "Rozszerzenie"])

if pdf and st.button("🚀 Generuj Notatki"):
    with st.spinner("Przetwarzam..."):
        # Wyciągnij tekst
        doc = fitz.open(stream=pdf.read(), filetype="pdf")
        tekst = ""
        for page in doc:
            tekst += page.get_text()
        
        # Prompt
        prompty = {
            "Skrót": "Skróć do najważniejszych punktów (max 30% długości):",
            "Zwykły": "Popraw formatowanie, zachowaj całą treść:",
            "Rozszerzenie": "Dodaj wyjaśnienia trudnych pojęć, usuń nieistotne:"
        }
        
        # Gemini - NOWA BIBLIOTEKA
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompty[tryb] + "\n\n" + tekst
        )
        notatki = response.text
        
        # Pokaż
        st.success("✅ Gotowe!")
        st.markdown(notatki)
        
        # Word do pobrania
        doc_word = Document()
        doc_word.add_heading('Notatki', 0)
        doc_word.add_paragraph(notatki)
        
        bio = io.BytesIO()
        doc_word.save(bio)
        
        st.download_button(
            "📥 Pobierz Word",
            bio.getvalue(),
            "notatki.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )