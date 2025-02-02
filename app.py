import streamlit as st
from utils import (
    DATA_INPUT,
    DEMO_PATIENTS,
    COLUMN_RATIO,
    initialize_page,
    typing_effect,
    get_discharge_report,
    get_date_options,
    filter_csv_by_id,
    display_patient_basic_info,
    display_patient_data,
    get_anamnesis_data,
    load_css,
    load_html,
    get_all_data_for_timeline,
    create_timeline,
    button_action,
    reset_button,
)


def main() -> None:
    initialize_page()
    st.title("Anamnesis Generator 🚀")
    load_css("static/base.css")

    column_1, column_2, column_3 = st.columns(COLUMN_RATIO)
    with column_1:
        # Selecting a patient
        st.session_state.patient = st.selectbox(
            label="Please select a patient:",
            options=DEMO_PATIENTS,
            index=None,
            placeholder="Patient...",
            on_change=reset_button,
        )
        patient_color = "green" if st.session_state.patient else "red"
        st.write(
            f"The following patient has been selected: :{patient_color}[{st.session_state.patient}]"
        )

        # Selecting standard
        st.session_state.standard = st.selectbox(
            label="Please select the anamnesis standard:",
            options=["WHO", "HU"],
            index=0,
            placeholder="Anamnesis standard...",
            on_change=reset_button,
        )
        standard_color = "green" if st.session_state.standard else "red"
        st.write(
            f"The following anamnesis standard has been selected: :{standard_color}[{st.session_state.standard}]"
        )

    with column_3:
        # Selecting a date
        if st.session_state.patient:
            date_options = get_date_options(st.session_state.patient)
            st.session_state.selected_date = st.selectbox(
                label="Please select the until date:",
                options=date_options,
                index=2,
                placeholder="Date...",
                on_change=reset_button,
            )
            date_color = "green" if st.session_state.selected_date else "red"
            st.write(
                f"The following date has been selected: :{date_color}[{st.session_state.selected_date}]"
            )

    if st.session_state.patient and st.session_state.selected_date:
        with st.expander("Patient Timeline"):
            plot_data = get_all_data_for_timeline(
                st.session_state.patient, st.session_state.selected_date
            )
            fig = create_timeline(plot_data)
            st.plotly_chart(fig)

    col1, col2, col3 = st.columns(COLUMN_RATIO)
    with col1:
        # If both inputs are provided present the Patient Data
        if st.session_state.patient and st.session_state.selected_date:
            # Present basic patient data
            basic_information = filter_csv_by_id(
                "data/patients.csv", st.session_state.patient, "Id"
            )
            display_patient_basic_info(basic_information)

            # Display detailed patient data
            for csv_data in DATA_INPUT:
                display_patient_data(
                    csv_data, st.session_state.patient, st.session_state.selected_date, True
                )

            with st.expander("Discharge report", expanded=False):
                discharge_report = get_discharge_report(st.session_state.patient, st.session_state.selected_date)
                st.write(discharge_report)

    with col3:
        # Create generate button
        if st.session_state.patient and st.session_state.selected_date:
            st.button("Generate", on_click=button_action)

        # If generate button is pressed
        if st.session_state.button_clicked:
            anamnesis = get_anamnesis_data(st.session_state.patient, st.session_state.selected_date)

            if not st.session_state.content:
                st.session_state.content = anamnesis

            # Check if anamnesis is available
            if not anamnesis:
                st.header("Generated Anamnesis:")
                st.subheader("There is no available anamnesis.")
                return
            else:
                st.header("Generated Anamnesis:")
                # In edit mode present the whole anamnesis in an editable text area
                if st.session_state.is_editing:
                    updated_content = st.text_area(
                        "Edit the content", st.session_state.content, height=1000
                    )
                    if st.button("Save"):
                        st.session_state.content = updated_content
                        st.session_state.is_editing = False
                        st.write("Content saved successfully!")
                        st.rerun()
                # Show the anamnesis as a typing effect first time if not in edit mode
                else:
                    if not st.session_state.typing_done and anamnesis:
                        typing_effect(st.session_state.content)
                        st.session_state.typing_done = True
                    else:
                        text_placeholder = st.empty()
                        text_placeholder.write(st.session_state.content)
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Edit"):
                            st.session_state.is_editing = True
                            st.rerun()
                    with c2:
                        st.download_button(
                            label="Download as .txt",
                            data=st.session_state.content,
                            file_name=f"{st.session_state.patient}_{st.session_state.selected_date[:10]}.txt",
                            mime="text/plain"
                        )
        else:
            st.session_state.typing_done = False
            st.session_state.content = ""
    st.markdown(load_html("templates/footer.html"), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
