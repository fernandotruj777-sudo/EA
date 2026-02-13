import os
import streamlit as st
from openai import OpenAI
import docx
import PyPDF2
from PIL import Image
import pytesseract

# 🔹 Configurar Tesseract para OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# 🔹 API Key segura desde los secretos de Streamlit
client = OpenAI(
    api_key=os.environ["OPENROUTER_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# ----------------------------
# FUNCIONES PARA LEER ARCHIVOS
# ----------------------------
def leer_docx(archivo):
    doc = docx.Document(archivo)
    texto = ""
    for parrafo in doc.paragraphs:
        texto += parrafo.text + "\n"
    return texto

def leer_pdf(archivo):
    lector = PyPDF2.PdfReader(archivo)
    texto = ""
    for pagina in lector.pages:
        texto += pagina.extract_text()
    return texto

def leer_imagen(archivo):
    imagen = Image.open(archivo)
    texto = pytesseract.image_to_string(imagen, lang="spa")
    return texto

# ----------------------------
# INTERFAZ
# ----------------------------
st.title("📚 Evaluador Universitario con Revisión APA")

# Selección de tipo de actividad
tipo_actividad = st.selectbox(
    "Tipo de actividad",
    [
        "Ensayo",
        "Línea del tiempo",
        "Cuadro SQA",
        "Tabla QQQ",
        "Mapa mental",
        "Cuadro sinóptico",
        "Foro"
    ]
)

# Rúbrica editable
rubrica_personalizada = st.text_area(
    "Pega aquí la rúbrica oficial de la universidad",
    height=300
)

# Subir archivo
archivo = st.file_uploader(
    "Sube el trabajo (Word, PDF, imagen)",
    type=["docx", "pdf", "png", "jpg", "jpeg"]
)

texto = ""

if archivo is not None:
    if archivo.name.endswith(".docx"):
        texto = leer_docx(archivo)
    elif archivo.name.endswith(".pdf"):
        texto = leer_pdf(archivo)
    else:
        texto = leer_imagen(archivo)

# Botón para evaluar
if st.button("Evaluar Documento"):
    if not texto:
        st.warning("Debes subir un archivo primero.")
    elif not rubrica_personalizada:
        st.warning("Debes pegar la rúbrica antes de evaluar.")
    else:
        prompt = f"""
Eres un profesor universitario experto en normas APA 7.

Evalúa el siguiente trabajo usando EXACTAMENTE esta rúbrica:

{rubrica_personalizada}

Respeta los criterios y ponderaciones indicadas.
Devuelve calificación por criterio y promedio final.

Trabajo:
{texto}

Devuelve el resultado así:
Ortografía: X
Contenido: X
Argumentación: X
Estructura: X
APA: X
Calificación Final: X

Después agrega retroalimentación detallada.
"""
        try:
            response = client.chat.completions.create(
                model="mistralai/mistral-7b-instruct",
                messages=[{"role": "user", "content": prompt}]
            )
            resultado = response.choices[0].message.content
            st.write(resultado)
        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
