import streamlit as st

# --- 1. CONFIGURARE PAGINĂ & STILIZARE ---
st.set_page_config(
    page_title="Obsidian Prompt Architect",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS pentru un look modern, "clean"
st.markdown("""
<style>
    /* Stiluri generale */
    .main {
        background-color: #0e1117;
    }
    h1 {
        color: #ff4b4b !important;
        font-weight: 800 !important;
    }
    h2, h3 {
        color: #e0e0e0 !important;
    }
    .stTextArea textarea {
        background-color: #262730;
        color: #ffffff;
        border-radius: 10px;
    }
    .stButton button {
        background-color: #ff4b4b;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #ff2b2b;
        border-color: #ff2b2b;
    }
    /* Highlight box pentru output */
    .output-box {
        padding: 20px;
        border-radius: 10px;
        background-color: #1e1e1e;
        border: 1px solid #444;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. TEMPLATE-URI DEFAULT (UNIVERSALE) ---

TEMPLATE_GHID = """Acționează ca un expert în {domain} și utilizator avansat de Obsidian.
Analizează textul următor extras din {source_name} și creează o pagină Obsidian formatată astfel:

### 1. YAML Header
Include:
* id: {id_format} (ex: {project_prefix}-{section}-Titlu)
* type: guideline-section
* project: {project_prefix}
* domain: {domain}
* tags: {default_tags}
* linked_paragraphs: (lasă gol)

### 2. Structură
* Callout: > [!abstract] Overview (rezumat scurt)
* Traducere: Redactează în limba {language}. Păstrează termenii tehnici consacrați ({exclude_terms}).
* Stil: Folosește subtitluri (H2, H3), bold, și emoji-uri pentru a structura informația.

### 3. Linking Logic
* Înlocuiește referințele numerice (ex: [27]) cu link-uri [[{ref_format}-AUTOR-AN]].
* Folosește lista bibliografică de la final pentru a identifica autorul și anul.

### 4. Input
TEXT SECȚIUNE:
{input_text}

BIBLIOGRAFIE:
{input_refs}
"""

TEMPLATE_STUDIU = """Acționează ca un expert cercetător în {domain}.
Creează o notă de referință academică pentru bibliografia de mai jos.

### 1. Header & ID
* H1: {ref_format}-AUTOR-AN
* YAML: id, type: reference, project: {project_prefix}, domain: {domain}, tags: {default_tags}, doi_url.

### 2. Conținut (Structură)
Caută detaliile sau extrage-le din text:
* Context/Population: Cine/Ce a fost studiat?
* Methods: Metodologia folosită.
* Results: Date cheie.
* Conclusion: Concluzia principală.
* Link Extern: DOI/PubMed.

### 3. Limba
Redactează în limba {language}.

### 4. Input
REFERINȚĂ:
{input_refs}
"""

# --- 3. SIDEBAR - CONTROL PARAMETRI ---
with st.sidebar:
    st.header("⚙️ Configurare Globală")
    
    mode = st.radio("Tip Generare:", ["Secțiune Ghid", "Notă Studiu/Ref"], index=0)
    
    st.markdown("---")
    st.subheader("Variabile Proiect")
    
    project_prefix = st.text_input("Prefix Proiect", "ESC-2025")
    domain = st.text_input("Domeniu Expertiză", "Cardiologie")
    language = st.selectbox("Limba Output", ["Română", "Engleză", "Franceză"])
    
    with st.expander("🛠️ Setări Avansate Formatare"):
        id_format = st.text_input("Format ID Ghid", f"{project_prefix}-X.X")
        ref_format = st.text_input("Format ID Referință", f"{project_prefix}-REF")
        exclude_terms = st.text_input("Termeni Netraduși", "Latină, Eponime, Medicamente")
        default_tags = st.text_input("Tag-uri implicite", "#guideline #medicine")

# --- 4. INTERFAȚA PRINCIPALĂ ---

st.title("🧠 Obsidian Prompt Architect")
st.markdown(f"Generează prompt-uri perfecte pentru **{domain}** ({project_prefix}).")

# Layout cu coloane pentru Input
col_input, col_config = st.columns([3, 2])

with col_input:
    st.subheader("📥 Date de Intrare")
    tab1, tab2 = st.tabs(["📄 Text Sursă", "📚 Bibliografie"])
    
    with tab1:
        if mode == "Secțiune Ghid":
            input_text = st.text_area("Lipește textul din PDF/Ghid aici:", height=300, placeholder="Ex: Section 3.1 Epidemiology...")
        else:
            st.info("Pentru modul 'Notă Studiu', introdu referința în tab-ul Bibliografie.")
            input_text = "N/A (Mode: Study)"

    with tab2:
        input_refs = st.text_area("Lipește Referințele Bibliografice:", height=300, placeholder="Ex: 1. Smith J, et al. European Heart Journal 2024...")

with col_config:
    st.subheader("📝 Editor Template")
    st.caption("Aici poți modifica 'Instrucțiunile Sistem' trimise către AI.")
    
    # Selectăm template-ul corect în funcție de mod
    current_template = TEMPLATE_GHID if mode == "Secțiune Ghid" else TEMPLATE_STUDIU
    
    # Text area editabil pentru template
    final_template_structure = st.text_area(
        "Editează structura promptului:", 
        value=current_template, 
        height=350
    )

# --- 5. LOGICA DE GENERARE ---

st.markdown("---")
generate_btn = st.button("🚀 GENEREAZĂ PROMPTUL AI", use_container_width=True)

if generate_btn:
    if not input_refs and (mode == "Notă Studiu/Ref"):
        st.error("⚠️ Te rog introdu cel puțin o referință bibliografică!")
    elif not input_text and (mode == "Secțiune Ghid"):
        st.error("⚠️ Te rog introdu textul secțiunii!")
    else:
        # Mapăm variabilele
        prompt_variables = {
            "domain": domain,
            "source_name": f"Ghidul {project_prefix}",
            "id_format": id_format,
            "project_prefix": project_prefix,
            "section": "SECTIUNE", # Placeholder
            "default_tags": default_tags,
            "language": language,
            "exclude_terms": exclude_terms,
            "ref_format": ref_format,
            "input_text": input_text,
            "input_refs": input_refs
        }
        
        # Umplem template-ul (Safe formatting pentru a evita erori la paranteze {} din textul userului)
        # Folosim .format() doar pe template-ul controlat de noi, nu pe textul userului direct
        try:
            final_prompt = final_template_structure.format(**prompt_variables)
            
            st.success("✅ Prompt generat cu succes! Copiază-l mai jos:")
            
            # Afișare output
            st.code(final_prompt, language="markdown")
            
            # Statistici rapide
            word_count = len(final_prompt.split())
            st.caption(f"Lungime Prompt: ~{word_count} cuvinte. Optimizat pentru GPT-4 / Claude 3.5 Sonnet.")
            
        except KeyError as e:
            st.error(f"Eroare în template: Variabila {e} lipsește din configurație. Verifică parantezele {{}}.")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Build for Obsidian Power Users • Design Universal
    </div>
    """, 
    unsafe_allow_html=True
)
