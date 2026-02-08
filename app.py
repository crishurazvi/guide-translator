import streamlit as st
import re

# Setare pagina wide
st.set_page_config(layout="wide", page_title="Medical Text Splitter for OneNote")

def pre_process_figures(text):
    """
    Cauta mentiuni despre Figuri/Tabele si adauga un marker vizual.
    """
    pattern = r"((?:Fig\.|Figure|Fig|Table|Tabelul|Schema)\s*\d+(\.\d+)?)"
    # Marker vizual puternic
    replacement = r"\1 \n\n🔴 [LASĂ LOC PENTRU: \1] \n\n"
    
    processed_text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return processed_text

def split_text_smartly(text, chunk_size):
    """
    Imparte textul in bucati mari fara a taia in mijlocul paragrafului.
    """
    paragraphs = text.split('\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        # Verificam daca adaugand paragraful depasim limita
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += para + "\n"
        else:
            chunks.append(current_chunk)
            current_chunk = para + "\n"
    
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def main():
    st.title("🧬 Medical Guidelines to OneNote")

    # 1. SETARI (Sidebar)
    with st.sidebar:
        st.header("⚙️ Setări")
        
        # Slider actualizat: default 15000, max 30000
        chunk_size = st.slider(
            "Mărime bucată text (caractere)", 
            min_value=1000, 
            max_value=30000, 
            value=15000, 
            step=1000,
            help="15.000 caractere = aprox 2000-3000 cuvinte per prompt."
        )
        
        target_lang = st.selectbox("Limba Traducerii", ["Română", "Engleză", "Franceză"])
        st.info("După ce lipești textul, apasă butonul 'Start Procesare' de sub casetă.")

    # 2. INPUT
    raw_text = st.text_area("Lipește textul medical (articol/guideline) aici:", height=300)

    # 3. BUTON DE ACTIUNE (Submit)
    # Folosim butonul ca trigger, altfel streamlit face rerun la fiecare caracter/blur
    process_btn = st.button("Start Procesare", type="primary")

    # 4. PROCESARE
    if process_btn and raw_text:
        # A. Identificare Figuri
        text_with_figures = pre_process_figures(raw_text)
        
        # B. Splituire
        chunks = split_text_smartly(text_with_figures, chunk_size=chunk_size)

        st.divider()
        st.subheader(f"✅ Rezultat: Text împărțit în {len(chunks)} părți")

        # Iteram prin chunks
        for i, chunk in enumerate(chunks):
            # Prompt MODIFICAT: Fara bullets fortate, accent pe formatare OneNote clean
            prompt_text = f"""Te rog să acționezi ca un expert medical și traducător.

SARCINA:
1. Traduce textul de mai jos în {target_lang}.
2. Păstrează terminologia medicală specifică în paranteză (în engleză/limba originală) acolo unde este crucial pentru precizie.
3. FORMAT PENTRU ONENOTE:
   - Folosește Titluri (Headings) și subtitluri clare.
   - Folosește **Bold** pentru a evidenția ideile principale.
   - Păstrează structura originală a paragrafelor (nu le transforma forțat în liste dacă nu sunt liste).
4. FIGURI ȘI TABELE:
   - Dacă întâlnești markerul "🔴 [LASĂ LOC PENTRU...]", te rog să pui o linie orizontală și să scrii textul bolduit și cu roșu (sau o notă clară), ca să știu să las spațiu liber pentru a insera manual imaginea.

TEXT DE TRADUS:
-----------------------
{chunk}
-----------------------
"""
            
            # Afisare rezultat
            label = f"PARTEA {i+1} din {len(chunks)} (Copiază acest prompt)"
            with st.expander(label, expanded=True):
                # st.code afiseaza butonul de copy automat
                st.code(prompt_text, language=None)
                st.caption(f"Lungime prompt: {len(prompt_text)} caractere")

if __name__ == "__main__":
    main()
