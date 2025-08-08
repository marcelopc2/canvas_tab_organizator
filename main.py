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

untouchable_tabs = ['home', 'settings']

# Función para procesar un curso individual
def process_course(course_id):
    local_errors = []
    try:
        course = canvas.get_course(course_id)
        current_tabs = course.get_tabs()
        tabs_dict = {tab.id: tab for tab in current_tabs}
        active_tab_ids = [t['id'] for t in active_tabs]

        # Activar pestañas deseadas
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

        # Ocultar todas las demás (excepto intocables)
        for tab_id, tab in tabs_dict.items():
            if tab_id not in active_tab_ids and tab_id not in untouchable_tabs:
                try:
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
