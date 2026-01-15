import streamlit as st
import fitz
from openai import OpenAI
from docx import Document
import io

# Konfiguracja
client = OpenAI(api_key=st.secrets["OPENAI_KEY"])

st.title("📚 Generator Notatek")

# Upload
pdf = st.file_uploader("Wrzuć PDF", type="pdf")

# Tryb
tryb = st.radio("Tryb:", ["Przepisz 1:1", "Skrót", "Rozszerzone z wyjaśnieniami"])

# Custom prompt
st.markdown("---")
st.subheader("🎯 Dodatkowe instrukcje (opcjonalnie)")
custom_prompt = st.text_area(
    "Np: 'Rozwiń temat elektrolitów, to moja słaba strona'",
    placeholder="Wpisz na czym Ci szczególnie zależy...",
    height=100
)

# Weryfikacja - tylko dla trybu rozszerzonego
if tryb == "Rozszerzone z wyjaśnieniami":
    weryfikacja = st.checkbox("✅ Sprawdź i popraw błędy + dodaj dodatkowe wyjaśnienia", value=True)
else:
    weryfikacja = False

if pdf and st.button("🚀 Generuj Notatki"):
    with st.spinner("Przetwarzam..."):
        # Wyciągnij tekst
        doc = fitz.open(stream=pdf.read(), filetype="pdf")
        tekst = ""
        for page in doc:
            tekst += page.get_text()
        
        # Prompt bazowy
        prompty = {
            "Przepisz 1:1": """Przepisz dokładnie tekst z tego materiału edukacyjnego do formatu notatek:

✓ Zachowaj CAŁĄ treść bez skracania
✓ Popraw tylko formatowanie (dodaj nagłówki, punktory gdzie pasują)
✓ Popraw ewentualne błędy ortograficzne
✓ NIE zmieniaj treści merytorycznej
✓ NIE dodawaj niczego od siebie

Materiał:""",
            
            "Skrót": """Przekształć ten materiał edukacyjny w zwięzłe notatki do nauki:

✓ Wyciągnij TYLKO najważniejsze informacje (30% oryginału)
✓ Użyj jasnych nagłówków i podpunktów
✓ Wytłuszcz kluczowe terminy
✓ Dodaj krótkie wyjaśnienia trudnych pojęć
✓ Formatuj w sposób ułatwiający zapamiętywanie

Materiał:""",
            
            "Rozszerzone z wyjaśnieniami": """Przekształć ten materiał edukacyjny w kompleksowe notatki do nauki:

✓ Zachowaj wszystkie ważne informacje
✓ DODAJ proste wyjaśnienia trudnych pojęć (jakbyś tłumaczył koledze)
✓ DODAJ praktyczne przykłady gdzie to możliwe
✓ Użyj analogii dla skomplikowanych tematów
✓ Strukturyzuj: nagłówki → podpunkty → wyjaśnienia
✓ Wytłuszcz najważniejsze terminy
✓ Usuń tylko organizacyjne info (daty sprawdzianów itp.)

Format idealny do nauki! Pisz jasno i przystępnie.

Materiał:"""
        }
        
        # Dodaj custom prompt jeśli jest
        prompt_finalny = prompty[tryb] + "\n\n" + tekst
        if custom_prompt.strip():
            prompt_finalny += f"\n\n⚠️ WAŻNE - zwróć szczególną uwagę na: {custom_prompt}"
        
        # Generuj notatki
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt_finalny}
            ]
        )
        notatki = response.choices[0].message.content
        
        # Weryfikacja i poprawa (opcjonalna)
        if weryfikacja:
            with st.spinner("Sprawdzam i poprawiam..."):
                verify_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "user", "content": f"""Zweryfikuj te notatki edukacyjne:

NOTATKI:
{notatki}

ORYGINAŁ:
{tekst}

ZADANIE:
1. Sprawdź czy są błędy merytoryczne
2. Dodaj wyjaśnienia tam gdzie może być niejasne
3. Upewnij się że format jest przyjazny do nauki
4. Jeśli coś ważnego pominięto - dodaj

Zwróć poprawioną wersję notatek."""}
                    ]
                )
                notatki = verify_response.choices[0].message.content
        
        # Pokaż
        st.success("✅ Gotowe!")
        st.markdown(notatki)
        
        # Word do pobrania
        doc_word = Document()
        doc_word.add_heading('Notatki', 0)
        
        # Dodaj info o trybie
        doc_word.add_paragraph(f"Tryb: {tryb}")
        if custom_prompt.strip():
            doc_word.add_paragraph(f"Dodatkowe instrukcje: {custom_prompt}")
        doc_word.add_paragraph("")  # Pusta linia
        
        doc_word.add_paragraph(notatki)
        
        bio = io.BytesIO()
        doc_word.save(bio)
        
        st.download_button(
            "📥 Pobierz Word",
            bio.getvalue(),
            "notatki.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )