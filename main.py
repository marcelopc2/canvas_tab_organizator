from decouple import config
import streamlit as st
from canvasapi import Canvas
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuración Canvas
BASE_URL = 'https://canvas.uautonoma.cl'
API_TOKEN = config('TOKEN')
canvas = Canvas(base_url=BASE_URL, access_token=API_TOKEN)

# Pestañas activas (visibles y ordenadas)
active_tabs = [
    {'id': 'home', 'position': 1},
    {'id': 'modules', 'position': 2},
    {'id': 'context_external_tool_644', 'position': 3},  # Libro de calificaciones
    {'id': 'people', 'position': 4},
    {'id': 'context_external_tool_225', 'position': 5},  # Zoom
    {'id': 'context_external_tool_1342', 'position': 6}, # Nuevas analíticas
]

hidden_priority_tabs = [
    {'id': 'assignments'},     
    {'id': 'quizzes'},         
    {'id': 'files'},  
    {'id': 'announcements'},        
    {'id': 'pages'}, 
    {'id': 'rubrics'},          
    {'id': 'syllabus'}, 
    {'id': 'discussions'},
    {'id': 'collaborations'},     
    {'id': 'outcomes'},
    {'id': 'search'},
    {'id': 'grades'},        
]

untouchable_tabs = ['home', 'settings']

# Función para procesar un curso individual
def process_course(course_id):
    local_errors = []
    try:
        course = canvas.get_course(course_id)
        current_tabs = course.get_tabs()
        tabs_dict = {tab.id: tab for tab in current_tabs}

        # 1) Activar y posicionar las pestañas "activas"
        for tab_info in active_tabs:
            tab_id = tab_info['id']
            position = tab_info['position']
            if tab_id in untouchable_tabs:
                continue
            if tab_id in tabs_dict:
                try:
                    tabs_dict[tab_id].update(hidden=False, position=position)
                except Exception as e:
                    local_errors.append(f"[Curso {course_id}] ⚠️ No se pudo activar '{tab_id}': {e}")
            else:
                local_errors.append(f"[Curso {course_id}] ❌ Pestaña no encontrada: {tab_id}")

        # 2) Posicionar pestañas ocultas importantes sin mostrarlas
        #    Las ponemos después de las activas para evitar colisiones.
        base_pos = (max([t['position'] for t in active_tabs]) if active_tabs else 0) + 1
        for offset, tab_info in enumerate(hidden_priority_tabs):
            tab_id = tab_info['id']
            desired_pos = base_pos + offset
            if tab_id in tabs_dict:
                try:
                    # Importante: las dejamos ocultas pero ordenadas
                    tabs_dict[tab_id].update(hidden=True, position=desired_pos)
                except Exception as e:
                    local_errors.append(f"[Curso {course_id}] ⚠️ No se pudo ordenar (oculta) '{tab_id}': {e}")
            # Si no existe en el curso, simplemente la ignoramos (no error visible)

        # 3) Mantener política de ocultar el resto (sin tocar su posición)
        active_tab_ids = [t['id'] for t in active_tabs]
        priority_hidden_ids = [t['id'] for t in hidden_priority_tabs]
        for tab_id, tab in tabs_dict.items():
            if tab_id in untouchable_tabs:
                continue
            if tab_id not in active_tab_ids and tab_id not in priority_hidden_ids:
                try:
                    # solo ocultamos (no tocamos position => quedan en el orden que estén)
                    tab.update(hidden=True)
                except Exception as e:
                    local_errors.append(f"[Curso {course_id}] ⚠️ No se pudo ocultar '{tab_id}': {e}")

    except Exception as e:
        local_errors.append(f"❗ Error al procesar el curso ID {course_id}: {e}")
    return local_errors

# Interfaz Streamlit
st.set_page_config(page_title="Organizador de pestañas", layout="wide", page_icon="⛑️")
st.title('Organizador de pestañas de cursos 👩‍🎓'.upper())
st.write(
    'Es una herramienta diseñada para organizar de manera masiva las pestañas de navegación de los '
    ':green[Cursos de Diplomados y Magísteres] en un formato estándar. Esto permite que las supervisoras '
    'de proyecto puedan acceder de forma más intuitiva y sencilla a las secciones de sus cursos, garantizando '
    'uniformidad y mejorando la experiencia de uso.'
)
st.markdown("""
### ℹ️ Cambios recientes:
- ✅ Se agregó **Libro de Calificaciones** (`/external_tools/644`)
- ✅ Se agregó **Nuevas Analíticas** (`/external_tools/1342`)
- ❌ Se quitó la pestaña **Calificaciones**
- 🚀 Se activó el procesamiento paralelo (multi-núcleo) para mayor velocidad
- ✅ Se Agrego un orden estándar a las pestañas ocultas (12-11-2025).
""")

course_ids_input = st.text_area('Ingresa los IDs de uno o más cursos separados por coma o espacio')

if st.button('Reordenar Pestañas'):
    course_ids = re.split(r'[,\s]+', course_ids_input.strip())
    course_ids = [cid for cid in course_ids if cid]

    if not course_ids:
        st.error('Por favor, ingresa al menos un ID de curso.')
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()
        error_messages = []
        total_courses = len(course_ids)

        # Ejecutar en paralelo con ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(process_course, cid): cid for cid in course_ids}

            for i, future in enumerate(as_completed(futures)):
                course_id = futures[future]
                status_text.text(f"✔️ Curso procesado: {course_id} ({i + 1}/{total_courses})")
                result_errors = future.result()
                error_messages.extend(result_errors)
                progress_bar.progress((i + 1) / total_courses)

        progress_bar.progress(1.0)

        # Mostrar errores al final
        if error_messages:
            st.subheader('❌ Resumen de errores y pestañas no encontradas:')
            for msg in error_messages:
                st.write(msg)
        else:
            status_text.text('✔️ Proceso completado sin errores. ¡Revisar cursos en Canvas!')
