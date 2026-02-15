import streamlit as st
import re

# --- 1. CONFIGURARE PAGINĂ & STILIZARE ---
st.set_page_config(
    page_title="Obsidian Prompt Architect",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    h1 { color: #ff4b4b !important; font-weight: 800 !important; }
    h2, h3 { color: #e0e0e0 !important; }
    .stTextArea textarea { background-color: #262730; color: #ffffff; border-radius: 10px; }
    .stButton button { background-color: #ff4b4b; color: white; font-weight: bold; border-radius: 8px; padding: 0.5rem 1rem; width: 100%; }
    .stButton button:hover { background-color: #ff2b2b; border-color: #ff2b2b; }
    .stExpander { background-color: #1e1e1e; border-radius: 8px; border: 1px solid #444; }
</style>
""", unsafe_allow_html=True)

# --- 2. TEMPLATE-URI DEFAULT ---

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
Output OBSIDIAN copy-paste ready; Foloseste formatari si emoji pentru a evidentia lucruri importante si a fi mai estetically pleasing;

### 1. Header & ID
* H1: {ref_format}-AUTOR-AN (sau @AutorAn conform convenției standard)
* YAML: 
    * id: (automat)
    * type: reference
    * project: {project_prefix}
    * linked_section: {parent_section_id}
    * tags: {default_tags}
    * doi_url: (extract form text)

### 2. Conținut (Structură)
Caută detaliile sau extrage-le din text:
* Context/Population: Cine/Ce a fost studiat?
* Methods: Metodologia folosită.
* Results: Date cheie.
* Conclusion: Concluzia principală.
* Disscution: Ce aport a adus acest studiu? Ce importanta are? De ce e citat in ghid? Ce intrebari a nascut acest studiu? 
* Link Extern: DOI/PubMed.
* Link Intern: {parent_section_id}

### 3. Limba
Redactează în limba {language}.

### 4. Input
REFERINȚĂ:
{input_refs}
"""

# --- 3. FUNCȚII AUXILIARE ---

def parse_references(text):
    """
    Împarte un text lung de bibliografie în referințe individuale.
    Presupune că fiecare referință nouă începe cu un număr la început de rând (ex: '34 ', '34\t', '34.').
    """
    lines = text.split('\n')
    chunks = []
    current_chunk = []
    
    # Regex pentru a detecta începutul unei referințe: Start de linie + Cifre + (Spațiu, Tab sau Punct)
    start_pattern = re.compile(r'^\d+[\.\t\s]')

    for line in lines:
        if start_pattern.match(line):
            # Dacă avem deja date în chunk-ul curent, le salvăm
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
            current_chunk.append(line)
        else:
            # Dacă nu e început de referință, adăugăm la chunk-ul curent (ex: rândurile cu Google Scholar)
            # Adăugăm doar dacă există un chunk activ (pentru a evita linii goale la început)
            if current_chunk or line.strip():
                 current_chunk.append(line)
    
    # Adăugăm ultimul chunk
    if current_chunk:
        chunks.append("\n".join(current_chunk))
        
    return chunks

# --- 4. SIDEBAR - CONTROL PARAMETRI ---
with st.sidebar:
    st.header("⚙️ Configurare Globală")
    
    mode = st.radio("Tip Generare:", ["Secțiune Ghid", "Notă Studiu/Ref"], index=0)
    
    st.markdown("---")
    st.subheader("Variabile Proiect")
    
    project_prefix = st.text_input("Prefix Proiect", "ESC-2025")
    domain = st.text_input("Domeniu Expertiză", "Cardiologie")
    language = st.selectbox("Limba Output", ["Română", "Engleză", "Franceză"])
    
    # Câmp nou pentru linkare
    parent_section_id = ""
    if mode == "Notă Studiu/Ref":
        st.markdown("---")
        st.info("🔗 Linking Logic")
        parent_section_id = st.text_input("ID Secțiune Ghid (Părinte)", placeholder="Ex: ESC-2025-3.3.2", help="Va crea un link în YAML către secțiunea de unde provine referința.")

    with st.expander("🛠️ Setări Avansate Formatare"):
        id_format = st.text_input("Format ID Ghid", f"{project_prefix}-X.X")
        ref_format = st.text_input("Format ID Referință", f"@{project_prefix}-REF") # Am actualizat default-ul
        exclude_terms = st.text_input("Termeni Netraduși", "Latină, Eponime, Medicamente")
        default_tags = st.text_input("Tag-uri implicite", "#guideline #medicine")

# --- 5. INTERFAȚA PRINCIPALĂ ---

st.title("🧠 Obsidian Prompt Architect")
st.markdown(f"Generează prompt-uri perfecte pentru **{domain}** ({project_prefix}).")

col_input, col_config = st.columns([3, 2])

with col_input:
    st.subheader("📥 Date de Intrare")
    tab1, tab2 = st.tabs(["📄 Text Sursă", "📚 Bibliografie"])
    
    with tab1:
        if mode == "Secțiune Ghid":
            input_text = st.text_area("Lipește textul din PDF/Ghid aici:", height=300, placeholder="Ex: Section 3.1 Epidemiology...")
        else:
            st.info("Modul 'Notă Studiu' activat. Folosește tab-ul Bibliografie.")
            input_text = "N/A"

    with tab2:
        placeholder_text = "34\tCaforio ALP... \n35\tImazio M..."
        input_refs = st.text_area("Lipește Referințele Bibliografice:", height=300, placeholder=placeholder_text)

with col_config:
    st.subheader("📝 Editor Template")
    current_template = TEMPLATE_GHID if mode == "Secțiune Ghid" else TEMPLATE_STUDIU
    final_template_structure = st.text_area("Editează structura promptului:", value=current_template, height=350)

# --- 6. LOGICA DE GENERARE ---

st.markdown("---")
generate_btn = st.button("🚀 GENEREAZĂ PROMPT(URI) AI", use_container_width=True)

if generate_btn:
    if not input_refs and (mode == "Notă Studiu/Ref"):
        st.error("⚠️ Te rog introdu referințele bibliografice!")
    elif not input_text and (mode == "Secțiune Ghid"):
        st.error("⚠️ Te rog introdu textul secțiunii!")
    else:
        # 1. Pregătim variabilele comune
        base_vars = {
            "domain": domain,
            "source_name": f"Ghidul {project_prefix}",
            "id_format": id_format,
            "project_prefix": project_prefix,
            "section": "SECTIUNE",
            "default_tags": default_tags,
            "language": language,
            "exclude_terms": exclude_terms,
            "ref_format": ref_format,
            "parent_section_id": parent_section_id if parent_section_id else "Unlinked"
        }

        # 2. Logică ramificată
        if mode == "Secțiune Ghid":
            # Caz simplu: 1 Prompt
            try:
                final_prompt = final_template_structure.format(
                    input_text=input_text,
                    input_refs=input_refs, # Toată biblio gramadă pentru context
                    **base_vars
                )
                st.success("✅ Prompt generat pentru Secțiune!")
                st.code(final_prompt, language="markdown")
            except KeyError as e:
                st.error(f"Eroare în template: Variabila {e} lipsește.")

        else:
            # Caz Complex: Notă Studiu -> Chunking
            chunks = parse_references(input_refs)
            
            if not chunks:
                st.warning("Nu am putut detecta referințe separate. Generez un singur prompt.")
                chunks = [input_refs]

            st.success(f"✅ Am detectat {len(chunks)} referințe. Generez {len(chunks)} prompt-uri separate:")
            
            # Iterăm prin fiecare referință și generăm prompt
            for i, chunk in enumerate(chunks):
                try:
                    prompt = final_template_structure.format(
                        input_refs=chunk, # Doar bucata curentă
                        input_text="N/A",
                        **base_vars
                    )
                    
                    # Extragem un preview mic din referință pentru titlul expanderului
                    preview = chunk.split('\n')[0][:80] + "..."
                    
                    with st.expander(f"Prompt #{i+1}: {preview}", expanded=(i==0)):
                        st.code(prompt, language="markdown")
                        
                except KeyError as e:
                    st.error(f"Eroare la referința #{i+1}: Variabila {e} lipsește.")

# --- FOOTER ---
st.markdown("---")
st.markdown("<div style='text-align: center; color: #666;'>Build for Obsidian Power Users • Design Universal</div>", unsafe_allow_html=True)
