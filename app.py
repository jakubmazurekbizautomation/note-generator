import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
from docx import Document
import io

# Konfiguracja
genai.configure(api_key=st.secrets["GEMINI_KEY"])

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
        
        # Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompty[tryb] + "\n\n" + tekst)
        notatki = response.text
        
        # Pokaż
        st.success("✅ Gotowe!")
        st.markdown(notatki)
        
        # Word do pobrania
        doc = Document()
        doc.add_heading('Notatki', 0)
        doc.add_paragraph(notatki)
        
        bio = io.BytesIO()
        doc.save(bio)
        
        st.download_button(
            "📥 Pobierz Word",
            bio.getvalue(),
            "notatki.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
```

**Plik 2: `requirements.txt`**
```
streamlit
PyMuPDF
google-generativeai
python-docx
