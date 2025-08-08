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
    {'id': 'grades', 'position': 3, 'hidden': False},
    {'id': 'people', 'position': 4, 'hidden': False},
    {'id': 'context_external_tool_225', 'position': 5, 'hidden': True},
    {'id': 'context_external_tool_1', 'position': 6, 'hidden': True},
    {'id': 'context_external_tool_262', 'position': 7, 'hidden': True},
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
    {'id': 'search', 'position': 27, 'hidden': True},
    {'id': 'context_external_tool_1342', 'position': 28, 'hidden': True},
]

st.set_page_config(page_title="PESTAÑAS ESPECIALIDADES MEDICAS".upper(), layout="wide", page_icon="⛑️")
st.title('PESTAÑAS ESPECIALIDADES MEDICAS 👩‍🎓')
st.info(f'Para ordenar las pestañas de los cursos de especialidades medicas.')
course_ids_input = st.text_area('Ingresa los IDs de uno o mas cursos separados por coma o espacio')

if st.button('Reordenar Pestañas'):
    # Separar y limpiar los IDs ingresados
    course_ids = re.split(r'[,\s]+', course_ids_input.strip())
    course_ids = [cid for cid in course_ids if cid]

    if not course_ids:
        st.error('Por favor, ingresa al menos un ID de curso.')
    else:
        progress_bar = st.progress(0)
        total_courses = len(course_ids)
        current_course = 0
        status_text = st.empty()
        status_text_tab = st.empty()
        error_messages = []

        for idx, course_id in enumerate(course_ids):
            try:
                course = canvas.get_course(course_id)
                current_course += 1
                status_text.text(f'Procesando curso {current_course}/{total_courses}:  {course.name} (ID: {course_id})')

                # Obtener las pestañas actuales del curso
                current_tabs = course.get_tabs()
                tabs_dict = {tab.id: tab for tab in current_tabs}

                # Actualizar pestañas según la configuración
                for tab_info in active_tabs:
                    tab_id = tab_info['id']
                    hidden = tab_info.get('hidden', None)
                    position = tab_info.get('position', None)
                    status_text_tab.text(f"Actualizando '{tab_id}'")
                    if tab_id in tabs_dict:
                        tab = tabs_dict[tab_id]
                        update_params = {}
                        if hidden is not None:
                            update_params['hidden'] = hidden
                        if position:
                            update_params['position'] = position
                        tab.update(**update_params)
                    else:
                        # por si necesito guardar los ids de pestañas no encontradas
                        pass

                # Actualizar la barra de progreso
                status_text_tab.text('')
                progress = (idx + 1) / total_courses
                progress_bar.progress(progress)
            except Exception as e:
                error_message = f'Error al procesar el curso ID {course_id}: {e}'
                error_messages.append(error_message)
                st.error(error_message)

        progress_bar.progress(1.0)

        # Mostrar mensajes de error al final, si los hay
        if error_messages:
            st.subheader('❌ Resumen de Errores (Contacta a Marcelo):')
            for msg in error_messages:
                st.write(msg)
        else:
            status_text.text('✔️ Proceso completado sin errores! - Revisar')