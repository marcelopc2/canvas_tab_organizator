from decouple import config
import streamlit as st
from canvasapi import Canvas
import re

BASE_URL = 'https://canvas.uautonoma.cl'
API_TOKEN = config('TOKEN')

canvas = Canvas(base_url=BASE_URL, access_token=API_TOKEN)

active_tabs = [
    # {'id': 'home', 'position': 1, 'hidden': False},
    {'id': 'modules', 'position': 2, 'hidden': False},
    {'id': 'people', 'position': 3, 'hidden': False},
    {'id': 'grades', 'position': 4, 'hidden': False},
    {'id': 'context_external_tool_225', 'position': 5, 'hidden': False},
    {'id': 'context_external_tool_1', 'position': 6, 'hidden': False},
    {'id': 'context_external_tool_262', 'position': 7, 'hidden': False},
    # Pestañas no visibles (posición no relevante)
    {'id': 'assignments', 'position': 8, 'hidden': True},
    {'id': 'quizzes', 'position': 9, 'hidden': True},
    {'id': 'files', 'position': 10, 'hidden': True},
    {'id': 'announcements', 'position': 11, 'hidden': True},
    {'id': 'pages', 'position': 12, 'hidden': True},
    {'id': 'rubrics', 'position': 13, 'hidden': True},
    {'id': 'syllabus', 'position': 14, 'hidden': True},
    {'id': 'discussions', 'position': 15, 'hidden': True},
    {'id': 'context_external_tool_644', 'position': 16, 'hidden': True},
    {'id': 'context_external_tool_35', 'position': 17, 'hidden': True},
    {'id': 'context_external_tool_56', 'position': 18, 'hidden': True},
    {'id': 'context_external_tool_1131', 'position': 19, 'hidden': True},
    {'id': 'conferences', 'position': 20, 'hidden': True},
    {'id': 'context_external_tool_36', 'position': 21, 'hidden': True},
    {'id': 'context_external_tool_171', 'position': 22, 'hidden': True},
    {'id': 'collaborations', 'position': 23, 'hidden': True},
    {'id': 'outcomes', 'position': 24, 'hidden': True},
    {'id': 'context_external_tool_167', 'position': 25, 'hidden': True},
    {'id': 'context_external_tool_1815', 'position': 26, 'hidden': True},
]

st.set_page_config(page_title="Organizador de pestañas", layout="wide", page_icon="⛑️")
st.title('Organizeitor de Diplomados 👩‍🎓')
st.write(f'Es una herramienta diseñada para organizar de manera masiva las pestañas de navegación de los :green[cursos de diplomados] en un formato estándar. Esto permite que las supervisoras de proyecto puedan acceder de forma más intuitiva y sencilla a las secciones de sus cursos, garantizando uniformidad y mejorando la experiencia de uso.')
course_ids_input = st.text_area('Ingresa los IDs de uno o mas cursos separados por coma o espacio')

if st.button('Ordenar pestañas'):
    # Separar y limpiar los IDs ingresados
    course_ids = re.split(r'[,\s]+', course_ids_input.strip())
    course_ids = [cid for cid in course_ids if cid]

    if not course_ids:
        st.error('Por favor, ingresa al menos un ID de curso.')
    else:
        progress_bar = st.progress(0)
        total_courses = len(course_ids)
        errors = 0
        good_ones = 0
        for idx, course_id in enumerate(course_ids):
            try:
                course = canvas.get_course(course_id)
                st.write(f'Procesando curso: {course.name} (ID: {course_id})')

                # Obtener las pestañas actuales del curso
                current_tabs = course.get_tabs()
                tabs_dict = {tab.id: tab for tab in current_tabs}

                # Actualizar pestañas según la configuración
                for tab_info in active_tabs:
                    tab_id = tab_info['id']
                    hidden = tab_info.get('hidden', False)
                    position = tab_info.get('position', None)

                    if tab_id in tabs_dict:
                        tab = tabs_dict[tab_id]
                        update_params = {'hidden': hidden}
                        if position:
                            update_params['position'] = position
                        tab.update(**update_params)
                        # st.write(f"Pestaña '{tab.label}' actualizada.")
                        good_ones += 1
                    else:
                        st.write(f"Pestaña '{tab_id}' no encontrada en el curso.")
                        errors += 1

                # Actualizar la barra de progreso
                progress_bar.progress((idx + 1) / total_courses)
            except Exception as e:
                st.error(f'Error al procesar el curso ID {course_id}: {e}')

        if errors == 0:
            st.success(f'Proceso completado sin errores ✔️ ({good_ones} pestañas ordenadas)')
        else:
            st.error(f'Proceso completado pero con fallas ❌ ({errors} pestañas con problemas)')