import streamlit as st
from logic import load_model, process_image, save_to_history, load_history, get_history_json, get_history_excel

st.set_page_config(
    page_title="Менеджер Парковки",
    page_icon="",
    layout="centered"
)

st.title("Менеджер Парковки")
st.markdown("Анализ загруженности парковки с использованием ИИ.")

st.divider()

st.subheader("Входные параметры")

col1, col2 = st.columns(2)

with col1:
    total_spaces = st.number_input(
        "Всего парковочных мест",
        min_value=1,
        value=50,
        step=1,
        help="Введите общее количество парковочных мест"
    )

with col2:
    uploaded_file = st.file_uploader(
        "Загрузить изображение парковки",
        type=["png", "jpg", "jpeg"],
        help="Загрузите изображение парковки для анализа"
    )

if uploaded_file is not None:
    st.image(uploaded_file, caption="Загруженное изображение", use_container_width=True)

st.divider()

if uploaded_file is not None:
    if st.button("Запустить обработку", type="primary", use_container_width=True):
        with st.spinner("Загрузка модели ИИ и обработка изображения..."):
            model = load_model()
            
            annotated_image, car_count = process_image(uploaded_file, model)
            
            free_spaces = max(0, total_spaces - car_count)
            occupancy_pct = (car_count / total_spaces) * 100 if total_spaces > 0 else 0
            
            st.session_state["last_result"] = {
                "annotated_image": annotated_image,
                "car_count": car_count,
                "free_spaces": free_spaces,
                "occupancy_pct": occupancy_pct,
                "filename": uploaded_file.name,
                "total_spaces": total_spaces
            }
            
            save_to_history({
                "filename": uploaded_file.name,
                "total_spaces": total_spaces,
                "detected_cars": car_count,
                "free_spaces": free_spaces,
                "occupancy_percentage": round(occupancy_pct, 2)
            })
            
            st.success("Обработка завершена!")

    if "last_result" in st.session_state:
        result = st.session_state["last_result"]
        
        st.subheader("Результаты")
        
        st.image(result["annotated_image"], caption="Обнаруженные автомобили", use_container_width=True)
        
        metric_cols = st.columns(4)
        
        with metric_cols[0]:
            st.metric("Всего мест", result["total_spaces"])
        
        with metric_cols[1]:
            st.metric("Обнаружено машин", result["car_count"])
        
        with metric_cols[2]:
            st.metric("Свободных мест", result["free_spaces"])
        
        with metric_cols[3]:
            st.metric("Загруженность", f"{result['occupancy_pct']:.1f}%")

else:
    st.warning("Пожалуйста, загрузите изображение для начала обработки.")

st.divider()

st.subheader("История запросов")

history_df = load_history()

if not history_df.empty:
    st.dataframe(history_df, use_container_width=True, hide_index=True)
    
    export_cols = st.columns(2)
    
    with export_cols[0]:
        st.download_button(
            label="Скачать JSON",
            data=get_history_json(),
            file_name="parking_history.json",
            mime="application/json",
            use_container_width=True
        )
    
    with export_cols[1]:
        st.download_button(
            label="Скачать Excel",
            data=get_history_excel(),
            file_name="parking_history.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
else:
    st.info("История пуста. Обработайте изображение, чтобы увидеть результаты.")
