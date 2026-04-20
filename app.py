import re
import json
import csv
import io
import random
import hashlib
from datetime import date, timedelta
from collections import Counter

import streamlit as st

# ════════════════════════════════════════════════════════════════════════════
#  ESTILOS PERSONALIZADOS
# ════════════════════════════════════════════════════════════════════════════
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Sora:wght@300;400;600;700&display=swap');

:root {
    --bg:        #0d1117;
    --surface:   #161b22;
    --surface2:  #21262d;
    --border:    #30363d;
    --accent:    #58a6ff;
    --accent2:   #3fb950;
    --warn:      #f0883e;
    --danger:    #f85149;
    --text:      #e6edf3;
    --muted:     #8b949e;
    --radius:    12px;
}

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
h1,h2,h3,h4 { font-family: 'Space Mono', monospace; }

.stApp { background: var(--bg); color: var(--text); }
section[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border); }

.stTabs [data-baseweb="tab-list"] { background: var(--surface); border-radius: var(--radius); padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; color: var(--muted); font-family: 'Space Mono', monospace; font-size:13px; }
.stTabs [aria-selected="true"] { background: var(--surface2) !important; color: var(--accent) !important; }

.stButton > button {
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text);
    border-radius: 8px;
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    transition: all .2s;
}
.stButton > button:hover { border-color: var(--accent); color: var(--accent); }

[data-testid="metric-container"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 12px 16px;
}

.stTextArea textarea, .stTextInput input {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: 'Sora', sans-serif !important;
}

.stSelectbox > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}

.flashcard {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 36px 40px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,.4);
    margin: 16px 0;
    transition: transform .2s;
}
.flashcard:hover { transform: translateY(-2px); }
.flashcard .label {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 16px;
}
.flashcard .content {
    font-size: 22px;
    font-weight: 600;
    color: var(--text);
    line-height: 1.5;
}
.flashcard .answer {
    font-size: 18px;
    color: var(--accent2);
    line-height: 1.6;
    margin-top: 8px;
}

.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.badge-easy   { background: rgba(31,111,235,.2);  color: #58a6ff; border:1px solid rgba(31,111,235,.4); }
.badge-medium { background: rgba(154,103,0,.2);   color: #e3b341; border:1px solid rgba(154,103,0,.4); }
.badge-hard   { background: rgba(185,28,28,.2);   color: #f85149; border:1px solid rgba(185,28,28,.4); }

.progress-wrap { background: var(--surface2); border-radius: 6px; height: 8px; overflow: hidden; margin: 8px 0; }
.progress-fill { height: 100%; border-radius: 6px; background: linear-gradient(90deg,var(--accent),var(--accent2)); transition: width .4s ease; }

hr { border: none; border-top: 1px solid var(--border); margin: 20px 0; }

.card-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
    margin: 8px 0;
}
.card-item .q { font-weight: 600; color: var(--accent); font-size: 15px; }
.card-item .a { color: var(--text); font-size: 14px; margin-top: 4px; }
</style>
"""


# ════════════════════════════════════════════════════════════════════════════
#  MOTOR DE GENERACIÓN DE FLASHCARDS
# ════════════════════════════════════════════════════════════════════════════

PATTERNS = [
    # ── ESPAÑOL ──────────────────────────────────────────────────────────
    (r"([\w\s\-ÁÉÍÓÚÜÑ]{2,50}?)\s+es\s+(?:un[ao]?\s+)([\w][\w\s\-,áéíóúüñÁÉÍÓÚÜÑ]{5,300})",
     "¿Qué es {0}?", "{1}"),
    (r"([\w\s\-ÁÉÍÓÚÜÑ]{2,40}?)\s+es\s+([\w][\w\s\-,áéíóúüñÁÉÍÓÚÜÑ]{8,300})",
     "¿Qué es {0}?", "{1}"),
    (r"([\w\s\-ÁÉÍÓÚÜÑ]{2,40}?)\s+permite\s+([\w][\w\s\-,áéíóúüñÁÉÍÓÚÜÑ]{8,300})",
     "¿Para qué sirve {0}?", "Permite {1}"),
    (r"([\w\s\-ÁÉÍÓÚÜÑ]{2,40}?)\s+se\s+define\s+como\s+([\w][\w\s\-,áéíóúüñÁÉÍÓÚÜÑ]{8,300})",
     "¿Cómo se define {0}?", "{1}"),
    (r"([\w\s\-ÁÉÍÓÚÜÑ]{2,40}?)\s+se\s+utiliza\s+para\s+([\w][\w\s\-,áéíóúüñÁÉÍÓÚÜÑ]{8,300})",
     "¿Para qué se utiliza {0}?", "Para {1}"),
    (r"([\w\s\-ÁÉÍÓÚÜÑ]{2,40}?)\s+consiste\s+en\s+([\w][\w\s\-,áéíóúüñÁÉÍÓÚÜÑ]{8,300})",
     "¿En qué consiste {0}?", "Consiste en {1}"),
    (r"([\w\s\-ÁÉÍÓÚÜÑ]{2,40}?)\s+tiene\s+como\s+objetivo\s+([\w][\w\s\-,áéíóúüñÁÉÍÓÚÜÑ]{8,300})",
     "¿Cuál es el objetivo de {0}?", "{1}"),
    (r"([\w\s\-ÁÉÍÓÚÜÑ]{2,40}?)\s+se\s+puede\s+(?:usar|utilizar)\s+para\s+([\w][\w\s\-,áéíóúüñÁÉÍÓÚÜÑ]{8,300})",
     "¿Para qué se puede usar {0}?", "{1}"),
    (r"([\w\s\-ÁÉÍÓÚÜÑ]{2,40}?)\s+(?:nació|naceu)\s+en\s+([\w][\w\s\-,áéíóúüñÁÉÍÓÚÜÑ]{3,150})",
     "¿Dónde nació {0}?", "En {1}"),
    (r"([\w\s\-ÁÉÍÓÚÜÑ]{2,40}?)\s+(?:publicó|publicou)\s+([\w][\w\s\-,áéíóúüñÁÉÍÓÚÜÑ]{5,300})",
     "¿Qué publicó {0}?", "{1}"),
    (r"([\w\s\-ÁÉÍÓÚÜÑ]{2,40}?)\s+(?:escribió|escribiu)\s+([\w][\w\s\-,áéíóúüñÁÉÍÓÚÜÑ]{5,300})",
     "¿Qué escribió {0}?", "{1}"),
    (r"([\w\s\-ÁÉÍÓÚÜÑ]{2,40}?)\s+(?:fundó|fundou)\s+([\w][\w\s\-,áéíóúüñÁÉÍÓÚÜÑ]{5,300})",
     "¿Qué fundó {0}?", "{1}"),
    (r"([\w\s\-ÁÉÍÓÚÜÑ]{2,40}?)\s+(?:ganó|gañou|recibiu|recibió)\s+(?:el\s+|o\s+|a\s+)?([\w][\w\s\-,áéíóúüñÁÉÍÓÚÜÑ]{5,300})",
     "¿Qué premio/reconocimiento recibió {0}?", "{1}"),
    (r"([\w\s\-ÁÉÍÓÚÜÑ]{2,40}?)\s+(?:caracteriza|caracterízase|se caracteriza)\s+por\s+([\w][\w\s\-,áéíóúüñÁÉÍÓÚÜÑ]{8,300})",
     "¿Cómo se caracteriza {0}?", "Se caracteriza por {1}"),
    # ── FLECHA: "Autor → obra" / "Corriente → descripción" ─────────────────
    (r"([\w\s\-ÁÉÍÓÚÜÑ]{2,40}?):\s+([\w][\w\s\-,\./:áéíóúüñÁÉÍÓÚÜÑ]{8,200})",
     "¿Qué se sabe de {0}?", "{1}"),
    # ── FORMATO APUNTES: "Concepto: descripción" ────────────────────────────
    # Lista de características/rasgos (respuesta puede tener "." entre items)
    (r"^(Características|Rasgos|Autores|Representantes|Obras|Temas|Tipos|Etapas):\s+([\w][\w\s\-,\./: ()áéíóúüñÁÉÍÓÚÜÑ]{15,400})",
     "¿Cuáles son las {0}?", "{1}"),
    # Género/Corriente/Movimiento con descripción
    (r"^(Género principal|Género|Corriente|Movimiento|Técnica|Estilo|Subtipo|Variante):\s+([\w][\w\s\-,\./: áéíóúüñÁÉÍÓÚÜÑ]{8,300})",
     "¿Qué es {0}?", "{1}"),
    # Patrón general "Concepto: descripción" — excluir palabras genéricas sueltas
    (r"^([A-ZÁÉÍÓÚÜÑa-záéíóúüñ][\w\s\-()ÁÉÍÓÚÜÑ]{3,50}?):\s+([\w][\w\s\-,\./: ()áéíóúüñÁÉÍÓÚÜÑ]{8,300})",
     "¿Qué significa {0}?", "{1}"),
    # ── INGLÉS ────────────────────────────────────────────────────────────
    (r"([\w\s\-]{2,40}?)\s+is\s+an?\s+([\w][\w\s\-,]{8,300})",
     "What is {0}?", "{0} is a/an {1}"),
    (r"([\w\s\-]{2,40}?)\s+(?:allows|enables)\s+([\w][\w\s\-,]{8,300})",
     "What does {0} allow/enable?", "It allows {1}"),
    (r"([\w\s\-]{2,40}?)\s+is\s+used\s+(?:for|to)\s+([\w][\w\s\-,]{8,300})",
     "What is {0} used for?", "It is used for {1}"),
]

STOPWORDS_ES = {
    # español
    "de","la","el","en","y","a","que","se","los","las","del","por","con","para",
    "un","una","es","al","lo","como","más","pero","sus","le","ya","o","este",
    "sí","porque","esta","entre","cuando","muy","sin","sobre","también","me",
    "hasta","hay","donde","quien","desde","todo","nos","durante","estados","todos",
    "uno","les","ni","contra","otros","ese","eso","ante","ellos","e","esto","mí",
    "antes","algunos","qué","unos","yo","otro","otras","son","mismo","así","cada",
    "ser","ha","su","bien","tanto","era","fue","han","si","según","fue","ser",
    "tema","temas","parte","tipo","tipos","forma","formas","caso","casos",
    "año","años","vez","veces","uso","usos","obra","obras",

    # inglés
    "the","of","and","to","in","is","it","its","or","are","was","for","on",
    "an","at","be","by","from","that","with","have","this","which","can","not",
    "will","all","has","but","been","they","were",
}

# Palabras genéricas que NO tienen sentido como base de una flashcard
BLACKLIST_FALLBACK = {
    "tema","temas","parte","tipo","cosa","cosas","forma","formas","caso","casos",
    "año","años","vez","veces","modo","modos","nivel","ejemplo","ejemplos",
    "outros","outras","primeiro","segundo","terceiro","fases","etapas","aspectos",
    "exemplos","exemplo","mostra","contidos","actividades",
    "problemas","factores","retornos","premios","autores","poetas","obras",
    "estilo","contexto","temas","lingua","linguas","formas","fases","anos",
    "españa","país","países","base","bases","línea","líneas","punto","puntos","elemento","elementos","nivel","niveles","eje","ejes","raíz","origen","causa","causas","efecto","efectos","medio","medios","tendencia","tendencias","corriente","corrientes","variante","variantes","enfoque","enfoques","perspectiva","perspectivas","modalidad","modalidades","técnica","técnicas","recurso","recursos","concepto","conceptos","noción","nociones","clave","claves","aspecto","aspectos","categoría","categorías",
    "cultura","poesía","narrativa","teatro","literatura",   # demasiado genéricas sin contexto
}


def _smart_fallback(sent: str) -> tuple:
    """
    Genera una flashcard inteligente a partir de una oración libre.
    Devuelve (question, answer) o (None, None) si no es útil.

    Estrategias por orden de preferencia:
    1. Sujeto + predicado largo → ¿Qué hizo/fue X?
    2. Nombre propio detectado → pregunta biográfica/temática
    3. Rechaza oraciones demasiado cortas o con keyword genérica
    """
    words = sent.split()
    if len(words) < 8:
        return None, None

    # Detectar nombre propio al principio (mayúscula, > 3 chars, no es inicio de párrafo)
    # Patrón: "NombrePropio verbo complemento…"
    m_biog = re.match(
        r'^([A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]{2,}(?:\s+[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]{2,}){0,3})'
        r'\s+(.{20,})',
        sent,
    )
    if m_biog:
        subject = m_biog.group(1).strip()
        predicate = m_biog.group(2).strip().rstrip('.')
        # Determinar tipo de pregunta por verbo
        if re.search(r'\b(?:nació)\b', predicate, re.I):
            return f"¿Dónde nació {subject}?", predicate
        if re.search(r'\b(?:publicó|escribió)\b', predicate, re.I):
            return f"¿Qué publicó/escribió {subject}?", predicate
        if re.search(r'\b(?:fundó|creó)\b', predicate, re.I):
            return f"¿Qué fundó/creó {subject}?", predicate
        if re.search(r'\b(?:es|fue|era)\b', predicate, re.I):
            return f"¿Qué es {subject}?", predicate
        # Genérico con nombre propio — vale la pena
        if len(subject.split()) >= 2 or len(subject) > 6:
            return f"¿Qué se sabe sobre {subject}?", sent.rstrip('.')

    # Buscar concepto técnico/específico en la oración (palabra larga única)
    candidates = [
        w for w in re.findall(r'\b[A-ZÁÉÍÓÚÜÑa-záéíóúüñ]{6,}\b', sent)
        if w.lower() not in STOPWORDS_ES
        and w.lower() not in BLACKLIST_FALLBACK
        and not w[0].islower()   # preferir sustantivos/nombres
    ]
    if not candidates:
        # buscar también minúsculas largas y técnicas
        candidates = [
            w for w in re.findall(r'\b[a-záéíóúüñ]{8,}\b', sent)
            if w.lower() not in STOPWORDS_ES and w.lower() not in BLACKLIST_FALLBACK
        ]

    if not candidates:
        return None, None

    # Tomar la palabra más larga (más específica)
    keyword = max(candidates, key=len)

    # Construir pregunta contextual, no genérica
    # Intentar extraer la parte de la oración que habla del concepto
    # Patrón: "… keyword … verbo … complemento"
    m_ctx = re.search(
        rf'({re.escape(keyword)}[\w\s\-,áéíóúüñÁÉÍÓÚÜÑ]{{0,60}})',
        sent, re.IGNORECASE
    )
    context_snippet = m_ctx.group(1).strip().rstrip('.,') if m_ctx else keyword

    question = f"¿Qué/Que é/es {keyword}?"
    answer   = sent.rstrip('.')
    return question, answer



def _is_bullet(line: str) -> bool:
    """True si la línea es un bullet de cualquier tipo."""
    return bool(re.match(r'^\s*[\*\-•o]\s+', line))


def _strip_bullet(line: str) -> str:
    """Quita el marcador de bullet y espacios."""
    return re.sub(r'^\s*[\*\-•o]\s+', '', line).strip()


def preprocess_outline(text: str) -> str:
    """
    Convierte apuntes en esquema a frases procesables.

    Reglas:
    - "Cabecera:\\n  * item" (cabecera termina en :) → "Cabecera: item1 / item2"  (una línea)
    - "Título corto\\n  * bullet con colon" (p.ej. nombre de autor) → cada bullet es su propia línea
    - Bullets sueltos → líneas directas
    - → se convierte en ": "
    - Secciones numeradas "1. Título" → se quita el número
    - Sub-bullets indentados → se adhieren al bullet padre con " / "
    """
    lines = text.splitlines()
    out = []
    i = 0

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        if not line:
            i += 1
            continue

        # ── Eliminar numeración de sección: "1.", "2.1.", etc. ───────────────
        m_num = re.match(r'^\s*\d+[\d\.]*\.?\s+(.+)', raw)
        if m_num:
            line = m_num.group(1).strip()
            raw  = line

        # ── Normalizar flechas ────────────────────────────────────────────────
        line = re.sub(r'\s*→\s*', ': ', line)
        raw  = line

        # ── Detectar si hay bullets en las líneas siguientes ─────────────────
        next_has_bullets = (
            i + 1 < len(lines) and _is_bullet(lines[i + 1])
        )

        # Cabecera explícita (termina en ":") → MERGE bullets en una sola línea
        if re.search(r':\s*$', line) and next_has_bullets:
            header = re.sub(r':\s*$', '', line).strip()
            items = []
            j = i + 1
            while j < len(lines):
                nxt_raw = lines[j]
                nxt = nxt_raw.strip()
                if not nxt:
                    j += 1
                    continue
                if _is_bullet(nxt_raw):
                    item = re.sub(r'\s*→\s*', ': ', _strip_bullet(nxt_raw))
                    # Sub-bullets indentados (≥3 espacios)
                    subs = []
                    k = j + 1
                    while k < len(lines):
                        sub = lines[k]
                        if len(sub) - len(sub.lstrip()) >= 3 and _is_bullet(sub):
                            subs.append(re.sub(r'\s*→\s*', ': ', _strip_bullet(sub)))
                            k += 1
                        else:
                            break
                    if subs:
                        item = item.rstrip(':.') + ": " + " / ".join(subs)
                    items.append(item.rstrip('.'))
                    j = k
                else:
                    break

            if items:
                out.append(header + ": " + " / ".join(items))
                i = j
            else:
                out.append(line)
                i += 1

        # Título corto SIN ":" seguido de bullets → emitir cada bullet por separado
        # (prefijado con el título como contexto)
        elif next_has_bullets and len(line.split()) <= 5 and not re.search(r'[.!?,;]', line):
            context = line
            j = i + 1
            while j < len(lines):
                nxt_raw = lines[j]
                nxt = nxt_raw.strip()
                if not nxt:
                    j += 1
                    continue
                if _is_bullet(nxt_raw):
                    item = re.sub(r'\s*→\s*', ': ', _strip_bullet(nxt_raw))
                    # Sub-bullets indentados
                    subs = []
                    k = j + 1
                    while k < len(lines):
                        sub = lines[k]
                        if len(sub) - len(sub.lstrip()) >= 3 and _is_bullet(sub):
                            subs.append(re.sub(r'\s*→\s*', ': ', _strip_bullet(sub)))
                            k += 1
                        else:
                            break
                    if subs:
                        item = item.rstrip(':.') + ": " + " / ".join(subs)
                    # Si el bullet ya tiene ": " → es "Concepto: desc" → línea propia
                    # Si no → prefijamos con el contexto
                    if ':' in item:
                        out.append(item.rstrip('.'))
                    else:
                        out.append(context + ": " + item.rstrip('.'))
                    j = k
                else:
                    # Línea no-bullet dentro del bloque → emitir normalmente
                    out.append(re.sub(r'\s*→\s*', ': ', nxt))
                    j += 1

            i = j

        # ── Bullet suelto (sin header previo capturado) ───────────────────────
        elif _is_bullet(raw):
            item = re.sub(r'\s*→\s*', ': ', _strip_bullet(raw))
            # Sub-bullets
            subs = []
            j = i + 1
            while j < len(lines):
                sub = lines[j]
                if len(sub) - len(sub.lstrip()) >= 3 and _is_bullet(sub):
                    subs.append(re.sub(r'\s*→\s*', ': ', _strip_bullet(sub)))
                    j += 1
                else:
                    break
            if subs:
                item = item.rstrip(':.') + ": " + " / ".join(subs)
            out.append(item)
            i = j

        # ── Línea normal ──────────────────────────────────────────────────────
        else:
            out.append(line)
            i += 1

    return "\n".join(out)


def clean_text(text: str) -> str:
    # Normalizar saltos de línea
    text = re.sub(r'\r\n', '\n', text)
    # Bullets "o " al inicio de línea → separador (apuntes esquema)
    text = re.sub(r'(?m)^\s*o\s+', '', text)
    # Listas numeradas tipo "1. " al inicio de línea
    text = re.sub(r'(?m)^\s*\d+\.\s+', '', text)
    # Caracteres raros (preservar \n para split)
    text = re.sub(r'[^\w\s\.,;:¿?¡!()\-/áéíóúüñÁÉÍÓÚÜÑ\n]', '', text)
    # Espacios múltiples en línea (no saltos)
    text = re.sub(r'[ \t]+', ' ', text)
    return text.strip()


def split_sentences(text: str) -> list:
    """
    Divide texto en segmentos procesables.
    Maneja tanto prosa (punto + mayúscula) como apuntes en esquema (saltos de línea).
    """
    # Paso 1: split por punto seguido de mayúscula (prosa)
    chunks = re.split(r'(?<=[.!?])[ \t]+(?=[A-ZÁÉÍÓÚÜÑ¿¡])', text)
    result = []
    for chunk in chunks:
        # Paso 2: cada chunk puede tener líneas de apuntes separadas por \n
        lines = re.split(r'\n+', chunk)
        for line in lines:
            line = line.strip()
            # Ignorar líneas vacías o demasiado cortas
            if len(line) < 20:
                continue
            # Ignorar líneas que son solo un título de sección sin contenido útil
            # (p.ej. "Realismo" solo, "Tema 1", "Características:")
            words = line.split()
            if len(words) <= 3 and not re.search(r'[:,]', line):
                continue
            result.append(line)
    return result


def extract_keywords(text: str, n: int = 5) -> list:
    # Números romanos que no sirven como keyword
    ROMAN = re.compile(r'^(?:M{0,4}(?:CM|CD|D?C{0,3})(?:XC|XL|L?X{0,3})(?:IX|IV|V?I{0,3}))$', re.I)
    words = re.findall(r'\b[A-ZÁÉÍÓÚÜÑ][a-záéíóúüñ]{3,}|[A-Z]{2,}\b', text)
    counts = Counter(
        w.lower() for w in words
        if w.lower() not in STOPWORDS_ES
        and w.lower() not in BLACKLIST_FALLBACK
        and not ROMAN.match(w)        # filtrar XIX, XX, etc.
        and len(w) >= 4               # mínimo 4 chars
    )
    return [w for w, _ in counts.most_common(n)]


def classify_difficulty(question: str, answer: str, source: str = "") -> str:
    """
    Clasifica usando la FUENTE COMPLETA, no solo el fragmento extraído.
    La fuente es la oración original, que contiene toda la densidad léxica.
    """
    # Evaluamos sobre la oración fuente (más rica) + respuesta extraída
    eval_text = source if source else (question + " " + answer)

    # 1. Longitud de la oración fuente
    src_words = len(eval_text.split())

    # 2. Términos técnicos / jerga especializada
    TECH = re.compile(
        r'\b[A-Z]{2,}\b'                                          # siglas
        r'|retropropagación|propagación|diferencial|gradiente'
        r'|covarianza|estocástic|autoregresiv|euclid|probabilístic'
        r'|normalización|regularización|distribución|proyect'
        r'|subespacios|subesp|embeddings|logits|softmax|queries'
        r'|hiperparámetro|parámetro|complejidad|cuadrática|lineal'
        r'|exponencial|aproximación|inferencia|latencia|cuantiz'
        r'|destilación|discriminador|generador|política|proximal'
        r'|feedforward|arquitectura|optimización|algoritmo|mecanismo'
        r'|transformer|neuronal|dimensión|vector|abstracto|función'
        r'|codifica|representa|escala|simetría|módulo|protocolo',
        re.IGNORECASE,
    )
    tech_count = len(TECH.findall(eval_text))

    # 3. Palabras largas (>= 10 chars) en la fuente
    long_words = sum(1 for w in eval_text.split() if len(re.sub(r'\W', '', w)) >= 10)

    # 4. Cláusulas subordinadas (ideas encadenadas)
    subordinates = len(re.findall(
        r'\bque\b|\bmediante\b|\brespecto\b|\bproporcional\b'
        r'|\blo que\b|\bde forma\b|\bpara ello\b|\bpor lo\b'
        r'|\bsin embargo\b|\bdebido a\b|\bpor tanto\b',
        eval_text, re.IGNORECASE,
    ))

    # 5. Comas = ideas compuestas
    commas = eval_text.count(',')

    # Scoring
    score = 0
    score += 2 if src_words > 45 else (1 if src_words > 25 else 0)
    score += 3 if tech_count >= 5 else (2 if tech_count >= 3 else (1 if tech_count >= 1 else 0))
    score += 2 if long_words >= 5 else (1 if long_words >= 2 else 0)
    score += 1 if subordinates >= 2 else 0
    score += 1 if commas >= 3 else 0

    if score <= 3:  return "fácil"
    if score <= 5:  return "media"
    return "difícil"


# Sujetos que NO deben convertirse en flashcard (cabeceras sin valor educativo)
SUBJECT_BLACKLIST = re.compile(
    r'^(tema\s+\d+|apartado|sección|bloque|unidad\s+\d|parte\s+\d|capítulo|'
    r'introducción|conclusión|resumen|índice|esquema|apuntes|nota|notas)$',
    re.IGNORECASE,
)


# ── Longitudes objetivo por tipo de pregunta ─────────────────────────────
#   definición simple    → 10-25 palabras
#   lista de ítems (·)   → máx 5 ítems, cada uno ≤ 12 palabras
#   explicación/proceso  → 20-45 palabras
_ANSWER_TARGETS = {
    "definition":  (10, 25),   # ¿Qué es X?
    "list":        (15, 60),   # ¿Cuáles son las X?
    "purpose":     (8,  25),   # ¿Para qué sirve/se utiliza X?
    "process":     (15, 40),   # ¿En qué consiste/Cómo se define X?
    "general":     (10, 35),   # resto
}

def _detect_answer_type(q_tpl: str) -> str:
    q = q_tpl.lower()
    if "cuáles son" in q:          return "list"
    if "qué es" in q or "significa" in q: return "definition"
    if "para qué" in q or "sirve" in q:   return "purpose"
    if "consiste" in q or "define" in q or "objetivo" in q: return "process"
    return "general"

def smart_trim_answer(answer: str, q_tpl: str) -> str:
    """
    Ajusta la respuesta a una longitud apropiada según el tipo de pregunta.
    Siempre corta en límite de PALABRA completa.
    """
    atype = _detect_answer_type(q_tpl)
    min_w, max_w = _ANSWER_TARGETS[atype]

    # ── Listas (·): máx 5 ítems, cada uno ≤ 10 palabras ─────────────────
    if " · " in answer:
        items = [i.strip() for i in answer.split(" · ") if i.strip()]
        trimmed = []
        for item in items[:5]:
            iw = item.split()
            trimmed.append(" ".join(iw[:10]) if len(iw) > 10 else item)
        return " · ".join(trimmed)

    # ── Texto libre ───────────────────────────────────────────────────────
    words = answer.split()
    n = len(words)

    if n <= min_w:
        return answer        # muy corto: no tocar

    if n <= max_w:
        return answer        # longitud perfecta

    # Demasiado largo → cortar en word boundary
    # Buscar la coma/punto más cercana ANTES de max_w (mínimo al 60%)
    candidate = " ".join(words[:max_w])
    for sep in (",", ";", "."):
        pos = candidate.rfind(sep)
        if pos > len(candidate) * 0.6:
            return candidate[:pos].rstrip()
    # Sin separador útil: cortar en la última palabra completa
    return " ".join(words[:max_w]).rstrip(" ,;.")

def generate_flashcards_from_text(text: str) -> list:
    text = preprocess_outline(text)   # primero: fusionar esquemas/bullets
    text = clean_text(text)
    sentences = split_sentences(text)
    cards = []
    seen_questions = set()

    for sent in sentences:
        generated = False
        for pat_idx, (pattern, q_tpl, a_tpl) in enumerate(PATTERNS):
            m = re.search(pattern, sent, re.IGNORECASE)
            if m:
                g = [gr.strip().rstrip('.,;') for gr in m.groups()]

                # Limpiar artículos iniciales gallegos/españoles del sujeto
                _ART = re.compile(r'^(?:O|A|Os|As|El|La|Los|Las|Un|Una|Uns|Unhas)\s+', re.IGNORECASE)
                if g:
                    g[0] = _ART.sub('', g[0]).strip()
                    if g[0]:
                        g[0] = g[0][0].upper() + g[0][1:]

                # Validar que el sujeto (g[0]) sea un sujeto real, no captura basura
                subject = g[0] if g else ""
                if len(subject.split()) > 6:
                    continue
                if re.search(r'\b(?:é|es|foi|fue|era|son|que|con|por|para|do|da)\b',
                             subject, re.IGNORECASE):
                    continue
                if len(subject) < 3 or subject.lower() in STOPWORDS_ES:
                    continue

                try:
                    question = q_tpl.format(*g)
                    answer   = a_tpl.format(*g)
                except IndexError:
                    continue
                # Limpiar respuesta de residuos de bullets/esquema
                answer = re.sub(r'^\s*o\s+', '', answer, flags=re.MULTILINE)
                answer = re.sub(r'\s+', ' ', answer).strip().rstrip('.,')
                # Quitar artefactos de plantilla
                answer = answer.replace('un/a ', '').replace('el/la ', '').strip()
                # Si la respuesta empieza repitiendo el sujeto, eliminarlo
                _subj = g[0].strip() if g else ""
                if _subj and len(_subj) > 4 and answer.lower().startswith(_subj[:20].lower()):
                    _vcut = re.search(
                        r'\b(es una|es un|es la|es el|permite|consiste|se utiliza|fue|es)\b',
                        answer, re.IGNORECASE)
                    if _vcut:
                        answer = answer[_vcut.start():].strip().capitalize()
                # Unir ítems "/" → "·"
                parts = [p.strip() for p in answer.split(' / ') if p.strip()]
                if len(parts) > 1:
                    answer = " · ".join(parts)
                # Ajustar longitud según tipo de pregunta
                answer = smart_trim_answer(answer, q_tpl)
                if len(question) < 10 or len(answer) < 5:
                    continue
                if len(answer.split()) < 3:
                    continue
                # Rechazar flashcards cuyo sujeto es solo un encabezado genérico
                subj = g[0].strip().lower() if g else ""
                if SUBJECT_BLACKLIST.match(subj):
                    continue
                # Rechazar sujetos demasiado cortos o que son frases numéricas
                if len(subj) < 5:
                    continue
                if re.match(r'^(un|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|\d+)\s', subj):
                    continue
                # Rechazar sujetos genéricos solo en el patrón colon genérico
                # (los patrones específicos como Características/Rasgos siempre pasan)
                if "significa" in q_tpl and subj in BLACKLIST_FALLBACK:
                    continue
                # Rechazar subjects tipo "autores y corrientes", "temas y subtemas"
                if "significa" in q_tpl and re.search(r'\by\b', subj):
                    continue
                # Deduplication key: question + first 40 chars of answer
                # (same question with different answers = different cards)
                q_key = hashlib.md5((question.lower() + answer[:40].lower()).encode()).hexdigest()[:8]
                if q_key in seen_questions:
                    continue
                seen_questions.add(q_key)
                difficulty = classify_difficulty(question, answer, source=sent)
                uid = hashlib.md5((question + answer).encode()).hexdigest()[:10]
                cards.append({
                    "id":           uid,
                    "question":     question.capitalize(),
                    "answer":       answer.capitalize(),
                    "difficulty":   difficulty,
                    "source":       sent[:80] + "…" if len(sent) > 80 else sent,
                    "interval":     1,
                    "next_review":  str(date.today()),
                    "correct":      0,
                    "wrong":        0,
                    "created_at":   str(date.today()),
                })
                generated = True
                break


    return cards


# ════════════════════════════════════════════════════════════════════════════
#  REPETICIÓN ESPACIADA (SM-2 simplificado)
# ════════════════════════════════════════════════════════════════════════════

def update_card_review(card: dict, known: bool) -> dict:
    if known:
        card["correct"] += 1
        card["interval"] = min(card["interval"] * 2, 60)
    else:
        card["wrong"] += 1
        card["interval"] = 1
    next_dt = date.today() + timedelta(days=card["interval"])
    card["next_review"] = str(next_dt)
    return card


def cards_due_today(cards: list) -> list:
    today = str(date.today())
    return [c for c in cards if c["next_review"] <= today]


# ════════════════════════════════════════════════════════════════════════════
#  EXPORTADORES
# ════════════════════════════════════════════════════════════════════════════

def export_markdown(cards: list) -> str:
    lines = ["# 🧠 Flashcards\n"]
    for i, c in enumerate(cards, 1):
        diff_emoji = {"fácil": "🟢", "media": "🟡", "difícil": "🔴"}.get(c["difficulty"], "⚪")
        lines.append(f"## {i}. {diff_emoji} {c['question']}\n")
        lines.append(f"**Respuesta:** {c['answer']}\n")
        lines.append(f"*Dificultad: {c['difficulty']}*\n\n---\n")
    return "\n".join(lines)


def export_csv(cards: list) -> str:
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["question","answer","difficulty","interval","correct","wrong"])
    writer.writeheader()
    for c in cards:
        writer.writerow({k: c[k] for k in ["question","answer","difficulty","interval","correct","wrong"]})
    return buf.getvalue()


def export_json(cards: list) -> str:
    return json.dumps(cards, ensure_ascii=False, indent=2)


# ════════════════════════════════════════════════════════════════════════════
#  HELPERS DE UI
# ════════════════════════════════════════════════════════════════════════════

DIFF_LABEL = {"fácil": "🟢 Fácil", "media": "🟡 Media", "difícil": "🔴 Difícil"}
DIFF_CLASS = {"fácil": "easy",      "media": "medium",   "difícil": "hard"}


def badge_html(difficulty: str) -> str:
    cls = DIFF_CLASS.get(difficulty, "easy")
    label = DIFF_LABEL.get(difficulty, difficulty)
    return f'<span class="badge badge-{cls}">{label}</span>'


def progress_bar(value: int, total: int) -> str:
    pct = int(value / total * 100) if total else 0
    return (
        f'<div class="progress-wrap">'
        f'<div class="progress-fill" style="width:{pct}%"></div></div>'
        f'<small style="color:var(--muted)">{value} / {total} ({pct}%)</small>'
    )


# ════════════════════════════════════════════════════════════════════════════
#  APP PRINCIPAL
# ════════════════════════════════════════════════════════════════════════════

def main():
    st.set_page_config(
        page_title="Flashcards IA",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # ── Estado global ────────────────────────────────────────────────────
    defaults = {
        "cards": [],
        "study_idx": 0,
        "study_revealed": False,
        "study_queue": [],
        "study_session_correct": 0,
        "study_session_wrong": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # ── Sidebar ──────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("## 🧠 Flashcards IA")
        st.markdown("---")
        total = len(st.session_state.cards)
        due   = len(cards_due_today(st.session_state.cards))
        easy  = sum(1 for c in st.session_state.cards if c["difficulty"] == "fácil")
        mid   = sum(1 for c in st.session_state.cards if c["difficulty"] == "media")
        hard  = sum(1 for c in st.session_state.cards if c["difficulty"] == "difícil")

        col1, col2 = st.columns(2)
        col1.metric("Total", total)
        col2.metric("Pendientes hoy", due)
        st.markdown(
            f"<div style='font-size:13px;color:var(--muted);margin-top:8px'>"
            f"🟢 {easy} fáciles &nbsp; 🟡 {mid} medias &nbsp; 🔴 {hard} difíciles</div>",
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.caption("Motor: reglas NLP + SM-2 espaciado")

        if total > 0 and st.button("🗑️ Borrar todas las cards", use_container_width=True):
            st.session_state.cards = []
            st.session_state.study_queue = []
            st.session_state.study_idx = 0
            st.rerun()

    # ── Tabs ─────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📥 Cargar contenido",
        "🃏 Mis flashcards",
        "🧠 Modo estudio",
        "📤 Exportar",
    ])

    # ╔═══════════════════════════════════╗
    # ║  TAB 1 — CARGAR CONTENIDO         ║
    # ╚═══════════════════════════════════╝
    with tab1:
        st.markdown("### Añade tu contenido de estudio")
        st.markdown(
            "<p style='color:var(--muted);font-size:14px'>"
            "El motor detecta conceptos en prosa, esquemas y bullets y genera preguntas automáticamente.</p>",
            unsafe_allow_html=True,
        )

        raw_text = st.text_area(
            "Texto",
            placeholder=(
                "Pega aquí tus apuntes. Funciona con:\n"
                "• Texto en prosa: 'X es una…', 'X permite…'\n"
                "• Esquemas con bullets (* o -)\n"
                "• Formato 'Concepto: descripción'\n"
                "• Secciones numeradas y sub-bullets"
            ),
            height=320,
            label_visibility="collapsed",
        )

        col_a, col_b = st.columns([2, 1])
        with col_b:
            diff_filter = st.multiselect(
                "Dificultad a generar",
                ["fácil", "media", "difícil"],
                default=["fácil", "media", "difícil"],
            )

        if st.button("⚡ Generar Flashcards", use_container_width=True, type="primary"):
            if not raw_text.strip():
                st.error("⚠️ Introduce texto antes de generar.")
            else:
                with st.spinner("Analizando texto y extrayendo conceptos…"):
                    new_cards = generate_flashcards_from_text(raw_text)
                    new_cards = [c for c in new_cards if c["difficulty"] in diff_filter]

                if not new_cards:
                    st.warning(
                        "No se detectaron patrones. Asegúrate de que el texto tenga frases como:\n"
                        "- *'X **es** una…'*, *'X **permite** …'*, *'X **se define como** …'*"
                    )
                else:
                    existing_ids = {c["id"] for c in st.session_state.cards}
                    added = [c for c in new_cards if c["id"] not in existing_ids]
                    st.session_state.cards.extend(added)

                    st.success(
                        f"✅ **{len(added)}** nuevas flashcards generadas "
                        f"({len(new_cards)-len(added)} duplicados omitidos)"
                    )
                    st.balloons()

                    st.markdown("#### Vista previa (primeras 5)")
                    for c in added[:5]:
                        st.markdown(
                            f'<div class="card-item">'
                            f'<div class="q">❓ {c["question"]}</div>'
                            f'<div class="a">💡 {c["answer"]}</div>'
                            f'<div style="margin-top:6px">{badge_html(c["difficulty"])}</div>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                    if len(added) > 5:
                        st.caption(f"… y {len(added)-5} más en la pestaña 🃏 Mis flashcards")

    # ╔═══════════════════════════════════╗
    # ║  TAB 2 — VER FLASHCARDS           ║
    # ╚═══════════════════════════════════╝
    with tab2:
        cards = st.session_state.cards
        if not cards:
            st.info("📭 Aún no tienes flashcards. Ve a **Cargar contenido** para generarlas.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                search = st.text_input("🔍 Buscar", placeholder="Filtra por texto…")
            with col2:
                diff_sel = st.selectbox("Dificultad", ["Todas", "fácil", "media", "difícil"])
            with col3:
                sort_by = st.selectbox("Ordenar por", ["Creación", "Dificultad", "Pendientes primero"])

            filtered = cards
            if search:
                filtered = [c for c in filtered
                            if search.lower() in c["question"].lower()
                            or search.lower() in c["answer"].lower()]
            if diff_sel != "Todas":
                filtered = [c for c in filtered if c["difficulty"] == diff_sel]
            if sort_by == "Dificultad":
                order = {"fácil": 0, "media": 1, "difícil": 2}
                filtered = sorted(filtered, key=lambda c: order.get(c["difficulty"], 0))
            elif sort_by == "Pendientes primero":
                today = str(date.today())
                filtered = sorted(filtered, key=lambda c: (c["next_review"] > today, c["next_review"]))

            st.markdown(
                progress_bar(
                    sum(1 for c in filtered if c["correct"] > c["wrong"]),
                    len(filtered)
                ),
                unsafe_allow_html=True,
            )
            st.caption(f"Mostrando {len(filtered)} de {len(cards)} cards")
            st.markdown("---")

            for c in filtered:
                card_map = {x["id"]: i for i, x in enumerate(st.session_state.cards)}
                with st.expander(f"**{c['question']}**  {badge_html(c['difficulty'])}", expanded=False):
                    st.markdown(
                        f'<div style="padding:12px 0">'
                        f'<p style="font-size:16px;color:var(--accent2)">💡 {c["answer"]}</p>'
                        f'<p style="font-size:12px;color:var(--muted)">'
                        f'Intervalo: {c["interval"]}d &nbsp;|&nbsp; '
                        f'Próxima revisión: {c["next_review"]} &nbsp;|&nbsp; '
                        f'✔ {c["correct"]} &nbsp; ✗ {c["wrong"]}</p>'
                        f'<details><summary style="font-size:12px;color:var(--muted);cursor:pointer">Fuente</summary>'
                        f'<p style="font-size:12px;color:var(--muted);font-style:italic">{c["source"]}</p>'
                        f'</details></div>',
                        unsafe_allow_html=True,
                    )
                    if st.button("🗑️ Eliminar", key=f"del_{c['id']}"):
                        st.session_state.cards = [x for x in st.session_state.cards if x["id"] != c["id"]]
                        st.rerun()

    # ╔═══════════════════════════════════╗
    # ║  TAB 3 — MODO ESTUDIO             ║
    # ╚═══════════════════════════════════╝
    with tab3:
        cards = st.session_state.cards
        if not cards:
            st.info("📭 Genera flashcards primero en **Cargar contenido**.")
        else:
            st.markdown("### ⚙️ Configurar sesión")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                study_mode = st.selectbox("Modo", [
                    "📅 Solo pendientes hoy (repetición espaciada)",
                    "🔀 Todas las cards (orden aleatorio)",
                    "🔴 Solo difíciles",
                ])
            with col_b:
                shuffle = st.checkbox("Mezclar orden", value=True)
            with col_c:
                st.markdown("<br>", unsafe_allow_html=True)
                start_btn = st.button("▶️ Iniciar sesión", use_container_width=True, type="primary")

            if start_btn:
                if "pendientes" in study_mode:
                    queue = cards_due_today(cards)
                elif "difíciles" in study_mode:
                    queue = [c for c in cards if c["difficulty"] == "difícil"]
                else:
                    queue = list(cards)

                if shuffle:
                    random.shuffle(queue)

                st.session_state.study_queue           = [c["id"] for c in queue]
                st.session_state.study_idx             = 0
                st.session_state.study_revealed        = False
                st.session_state.study_session_correct = 0
                st.session_state.study_session_wrong   = 0

                if not queue:
                    st.warning("No hay cards para este filtro.")

            st.markdown("---")

            queue_ids = st.session_state.study_queue
            idx       = st.session_state.study_idx

            if queue_ids and idx >= len(queue_ids):
                sc = st.session_state.study_session_correct
                sw = st.session_state.study_session_wrong
                total_s = sc + sw
                pct = int(sc / total_s * 100) if total_s else 0
                emoji = '🏆' if pct >= 80 else '💪' if pct >= 50 else '📚'
                st.markdown(
                    f'<div class="flashcard">'
                    f'<div class="label">SESIÓN COMPLETADA 🎉</div>'
                    f'<div class="content" style="font-size:48px">{emoji}</div>'
                    f'<div class="answer">'
                    f'{sc} correctas &nbsp;·&nbsp; {sw} falladas &nbsp;·&nbsp; {pct}% acierto'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )
                if st.button("🔄 Nueva sesión", use_container_width=True):
                    st.session_state.study_queue = []
                    st.session_state.study_idx   = 0
                    st.rerun()

            elif queue_ids:
                current_id = queue_ids[idx]
                card_map   = {c["id"]: i for i, c in enumerate(st.session_state.cards)}
                c_idx      = card_map.get(current_id)

                if c_idx is None:
                    st.session_state.study_idx += 1
                    st.rerun()

                c = st.session_state.cards[c_idx]

                st.markdown(progress_bar(idx, len(queue_ids)), unsafe_allow_html=True)
                st.markdown(
                    f"<p style='color:var(--muted);font-size:13px;text-align:center'>"
                    f"Card {idx+1} de {len(queue_ids)} &nbsp;·&nbsp; {badge_html(c['difficulty'])}</p>",
                    unsafe_allow_html=True,
                )

                if not st.session_state.study_revealed:
                    st.markdown(
                        f'<div class="flashcard">'
                        f'<div class="label">❓ PREGUNTA</div>'
                        f'<div class="content">{c["question"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button("👁️ Ver respuesta", use_container_width=True):
                        st.session_state.study_revealed = True
                        st.rerun()
                else:
                    st.markdown(
                        f'<div class="flashcard">'
                        f'<div class="label">❓ PREGUNTA</div>'
                        f'<div class="content">{c["question"]}</div>'
                        f'<hr style="border-color:var(--border);margin:16px 0">'
                        f'<div class="label">💡 RESPUESTA</div>'
                        f'<div class="answer">{c["answer"]}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    col_ok, col_no = st.columns(2)
                    with col_ok:
                        if st.button("✅ Lo sabía", use_container_width=True):
                            st.session_state.cards[c_idx] = update_card_review(c, known=True)
                            st.session_state.study_session_correct += 1
                            st.session_state.study_idx     += 1
                            st.session_state.study_revealed = False
                            st.rerun()
                    with col_no:
                        if st.button("❌ No lo sabía", use_container_width=True):
                            st.session_state.cards[c_idx] = update_card_review(c, known=False)
                            st.session_state.study_session_wrong += 1
                            st.session_state.study_idx     += 1
                            st.session_state.study_revealed = False
                            st.rerun()
            else:
                st.info("Configura y lanza una sesión usando los controles de arriba ☝️")

    # ╔═══════════════════════════════════╗
    # ║  TAB 4 — EXPORTAR                 ║
    # ╚═══════════════════════════════════╝
    with tab4:
        cards = st.session_state.cards
        if not cards:
            st.info("📭 No hay flashcards que exportar.")
        else:
            st.markdown("### Exportar flashcards")
            st.markdown(
                f"<p style='color:var(--muted)'>Tienes <strong>{len(cards)}</strong> cards listas para exportar.</p>",
                unsafe_allow_html=True,
            )

            export_diff = st.multiselect(
                "Filtrar por dificultad",
                ["fácil", "media", "difícil"],
                default=["fácil", "media", "difícil"],
            )
            export_cards = [c for c in cards if c["difficulty"] in export_diff]
            st.caption(f"{len(export_cards)} cards seleccionadas")
            st.markdown("---")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("#### 📄 Markdown")
                st.caption("Para Obsidian, Notion, apuntes")
                md = export_markdown(export_cards)
                st.download_button("⬇️ Descargar .md", data=md,
                                   file_name="flashcards.md", mime="text/markdown",
                                   use_container_width=True)
                with st.expander("Vista previa"):
                    st.code(md[:500] + "…", language="markdown")
            with col2:
                st.markdown("#### 📊 CSV (Anki)")
                st.caption("Compatible con importación Anki")
                csv_data = export_csv(export_cards)
                st.download_button("⬇️ Descargar .csv", data=csv_data,
                                   file_name="flashcards.csv", mime="text/csv",
                                   use_container_width=True)
                with st.expander("Vista previa"):
                    st.code(csv_data[:500] + "…", language="text")
            with col3:
                st.markdown("#### 📦 JSON")
                st.caption("Para reutilizar en otros proyectos")
                json_data = export_json(export_cards)
                st.download_button("⬇️ Descargar .json", data=json_data,
                                   file_name="flashcards.json", mime="application/json",
                                   use_container_width=True)
                with st.expander("Vista previa"):
                    st.code(json_data[:500] + "…", language="json")

            st.markdown("---")
            st.markdown("#### 📈 Estadísticas de aprendizaje")
            total_c  = sum(c["correct"] for c in export_cards)
            total_w  = sum(c["wrong"]   for c in export_cards)
            total_rw = total_c + total_w
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            col_s1.metric("Revisiones totales", total_rw)
            col_s2.metric("Correctas", total_c)
            col_s3.metric("Falladas", total_w)
            col_s4.metric("Tasa de acierto",
                          f"{int(total_c/total_rw*100) if total_rw else 0}%")

            hard_cards = sorted(export_cards, key=lambda c: c["wrong"], reverse=True)[:5]
            if any(c["wrong"] > 0 for c in hard_cards):
                st.markdown("##### 🔴 Cards con más errores")
                for c in hard_cards:
                    if c["wrong"] > 0:
                        st.markdown(
                            f'<div class="card-item">'
                            f'<div class="q">❓ {c["question"]}</div>'
                            f'<small style="color:var(--danger)">✗ {c["wrong"]} errores</small>'
                            f'</div>',
                            unsafe_allow_html=True,
                        )


if __name__ == "__main__":
    main()
