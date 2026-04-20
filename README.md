# 🧠 Flashcards IA

Generador automático de flashcards a partir de texto usando reglas de NLP + repetición espaciada (SM-2 simplificado).

Convierte apuntes en preguntas y respuestas listas para estudiar.

## 🚀 Características
- 🧠 Generación automática de flashcards desde:
  - texto en prosa
  - esquemas
  - bullets (*, -)
  - formato Concepto: descripción
- 🌍 Soporte multilenguaje:
  - Español
  - Inglés
- 🎯 Clasificación automática de dificultad:
  - Fácil
  - Media
  - Difícil
- 🔁 Sistema de repetición espaciada (SM-2 simplificado)
- 📊 Modo estudio interactivo
- 📤 Exportación a:
  - Markdown
  - CSV (compatible con Anki mediante mapeo)
  - JSON
## 🏗️ Cómo funciona
- Pipeline simplificado:
  - Texto → Preprocesado → Segmentación → Patrones NLP → Flashcards
- Componentes principales
  - preprocess_outline() → Convierte esquemas en texto procesable
  - generate_flashcards_from_text() → Motor principal de generación
  - classify_difficulty() → Clasificación automática de dificultad
  - update_card_review() → Lógica de repetición espaciada
## ⚙️ Instalación
git clone https://github.com/Kevin-2099/Flashcards-IA

cd Flashcards-IA

pip install -r requirements.txt

streamlit run app.py
## 🧩 Uso
Ejecuta la app

Ve a Cargar contenido

Pega tus apuntes

Genera flashcards

Estudia en modo repetición espaciada
## 📊 Dificultad
- Se calcula automáticamente usando:
  - longitud del texto
  - términos técnicos
  - complejidad sintáctica
  - número de cláusulas
## ⚠️ Limitaciones
Basado en reglas (no usa modelos de IA)

Depende de la calidad del texto de entrada

No entiende contexto profundo
## 📄 Licencia

Este proyecto se distribuye bajo una **licencia propietaria con acceso al código (source-available)**.

El código fuente se pone a disposición únicamente para fines de **visualización, evaluación y aprendizaje**.

❌ No está permitido copiar, modificar, redistribuir, sublicenciar, ni crear obras derivadas del software o de su código fuente sin autorización escrita expresa del titular de los derechos.

❌ El uso comercial del software, incluyendo su oferta como servicio (SaaS), su integración en productos comerciales o su uso en entornos de producción, requiere un **acuerdo de licencia comercial independiente**.

📌 El texto **legalmente vinculante** de la licencia es la versión en inglés incluida en el archivo `LICENSE`. 

Se proporciona una traducción al español en `LICENSE_ES.md` únicamente con fines informativos. En caso de discrepancia, prevalece la versión en inglés.

## Autor
Kevin-2099
