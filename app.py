import streamlit as st
import re

# Setare pagina pentru a fi wide (mai mult spatiu)
st.set_page_config(layout="wide", page_title="Medical Text Splitter for OneNote")

def pre_process_figures(text):
    """
    Cauta mentiuni despre Figuri/Tabele si adauga un marker vizual
    pentru a sti unde sa lasi spatiu in OneNote.
    """
    # Regex pentru a gasi "Fig 1", "Figure 2.1", "Table 3", etc.
    # Pattern-ul cauta cuvinte cheie urmate de numere/litere
    pattern = r"((?:Fig\.|Figure|Fig|Table|Tabelul|Schema)\s*\d+(\.\d+)?)"
    
    # Inlocuim gasirea cu textul original + markerul vizual
    # Markerul este facut sa fie evident pentru ChatGPT sa il pastreze
    replacement = r"\1 \n\n🔴🔴🔴 [LIPESTE IMAGINEA/SCHEMA AICI: \1] 🔴🔴🔴\n\n"
    
    processed_text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return processed_text

def split_text_smartly(text, chunk_size=3000):
    """
    Imparte textul in bucati, incercand sa nu taie frazele la jumatate.
    Se opreste la paragrafe (\n).
    """
    paragraphs = text.split('\n')
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += para + "\n"
        else:
            chunks.append(current_chunk)
            current_chunk = para + "\n"
    
    if current_chunk:
        chunks.append(current_chunk)
        
    return chunks

def main():
    st.title("🧬 Medical Guidelines to OneNote - AI Prepper")
    st.markdown("""
    **Instrucțiuni:**
    1. Lipește textul din guideline/articol medical în cutia de mai jos.
    2. Aplicația va detecta automat unde sunt figuri ("Figure X", "Table Y") și va marca locul.
    3. Copiază pe rând bucățile generate ("PROMPTS") și dă-le la ChatGPT.
    4. ChatGPT va traduce și formata totul gata de Copy-Paste în OneNote.
    """)

    # Sidebar pentru setari
    with st.sidebar:
        st.header("⚙️ Setări")
        chunk_size = st.slider("Mărime bucată text (caractere)", 1000, 8000, 3000, help="3000 este optim pentru GPT-4")
        target_lang = st.selectbox("Limba Traducerii", ["Română", "Engleză (Summarized)", "Franceză"])
        
    # Zona de input
    raw_text = st.text_area("Lipește textul medical aici:", height=300)

    if raw_text:
        # Pasul 1: Identificam figuri si adaugam markers
        text_with_figures = pre_process_figures(raw_text)
        
        # Pasul 2: Impartim textul in bucati logice
        chunks = split_text_smartly(text_with_figures, chunk_size=chunk_size)

        st.divider()
        st.subheader(f"✅ Rezultat: {len(chunks)} părți de copiat")

        # Iteram prin chunks
        for i, chunk in enumerate(chunks):
            # Construim prompt-ul pentru ChatGPT
            
            base_prompt = f"""Te rog să acționezi ca un expert medical și traducător.
Sarcina ta este:
1. Să traduci textul de mai jos în {target_lang} (păstrează terminologia medicală în engleză în paranteze unde este relevant).
2. Să formatezi ieșirea special pentru a fi dată Copy-Paste în **Microsoft OneNote**. Asta înseamnă:
   - Folosește titluri clare (Bold și font mai mare dacă poți).
   - Folosește liste cu puncte (Bullet points) ierarhice pentru a structura informația.
   - Folosește **Bold** pentru concepte cheie.
3. Foarte IMPORTANT: Dacă în text vezi markerul "🔴🔴🔴 [LIPESTE IMAGINEA...]", te rog să pui o linie orizontală și să scrii textul respectiv bolduit și cu o culoare roșie sau galbenă, ca să știu să las spațiu liber pentru screenshot.

Textul de tradus:
-----------------------
{chunk}
-----------------------
"""
            
            with st.expander(f"Partea {i+1} / {len(chunks)} (Apasă pentru detalii)", expanded=True):
                st.info("Copiază textul de mai jos (blocul gri) și dă-i Paste în ChatGPT.")
                
                # Afisam direct intr-un code block care are buton de Copy integrat in Streamlit
                st.code(base_prompt, language=None)
                
                # Previzualizare text original (optional, pentru verificare)
                with st.popover("Vezi textul original din această secțiune"):
                    st.text(chunk)

if __name__ == "__main__":
    main()

În câteva secunde vei avea link-ul tău privat unde poți procesa guidelines oricând ai nevoie.
