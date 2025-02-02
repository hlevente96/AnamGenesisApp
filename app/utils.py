import pandas as pd
import streamlit as st
import time
import re
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os

COLUMN_RATIO = [6, 1, 6]
DATA_INPUT = [
    "procedures",
    "observations",
    "medications",
    "immunizations",
    "imaging_studies",
    "encounters",
    "conditions",
    "careplans",
    "allergies",
]
DEMO_PATIENTS = [
    "30a6452c-4297-a1ac-977a-6a23237c7b46",
    "37c177ea-4398-fb7a-29fa-70eb3d673876",
    "b05fba34-1719-c0de-ac25-16e65de3d26a",
]
DEMO_PATIENTS_TIMES = {
    "30a6452c-4297-a1ac-977a-6a23237c7b46":[
        "2015-10-31T11:02:48Z",
        "2020-10-30T11:02:48Z",
        "2022-05-01T09:04:48Z",
    ],
    "37c177ea-4398-fb7a-29fa-70eb3d673876":[
        "2017-10-21T23:25:32Z",
        "2020-04-24T00:34:38Z",
        "2024-10-03T23:42:53Z",
    ],
    "b05fba34-1719-c0de-ac25-16e65de3d26a":[
        "2016-02-14T06:56:41Z",
        "2019-08-28T12:04:41Z",
        "2023-09-24T09:04:41Z",
    ],
}


def initialize_page() -> None:
    st.set_page_config(page_title="Anamnesis Generator", page_icon="🏥", layout="wide")

    if "patient" not in st.session_state:
        st.session_state.patient = None
    if "selected_date" not in st.session_state:
        st.session_state.selected_date = None
    if "is_editing" not in st.session_state:
        st.session_state.is_editing = False
    if "content" not in st.session_state:
        st.session_state.content = ""
    if "typing_done" not in st.session_state:
        st.session_state.typing_done = False
    if "standard" not in st.session_state:
        st.session_state.standard = ""
    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = False


def button_action() -> None:
    st.session_state.button_clicked = True


def reset_button() -> None:
    st.session_state.button_clicked = False


def load_css(file_name: str):
    file_path = os.path.join(os.path.dirname(__file__), 'static', file_name)
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def load_html(file_name: str):
    file_path = os.path.join(os.path.dirname(__file__), 'templates', file_name)
    with open(file_path, "r") as file:
        html_content = file.read()
    return html_content


def typing_effect(text, speed=0.0005) -> None:
    placeholder = st.empty()
    for i in range(1, len(text) + 1):
        placeholder.write(text[:i])
        time.sleep(speed)


def get_date_options(patient: str) -> list:
    available_times = DEMO_PATIENTS_TIMES[patient]
    formatted_times = [
        datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d at %I:%M:%S %p")
        for date_time in available_times
    ]
    return formatted_times


def get_column_from_csv(file_path: str, column_name: str) -> list:
    df = pd.read_csv(file_path)
    return df[column_name].tolist()


def filter_csv_by_id(file_name: str, column_value: str, column_name: str) -> pd.DataFrame:
    file_path = os.path.join(os.path.dirname(__file__), 'data', file_name)
    df = pd.read_csv(file_path)
    if column_name not in df.columns:
        raise ValueError(f"The dataset does not have a {column_name} column.")
    return df[df[column_name] == column_value]


def get_discharge_report(patient: str, date: str) -> str:
    date = pd.to_datetime(date).tz_localize(None)
    discharge_reports = filter_csv_by_id(
        "discharge_reports_generated.csv", patient, "PATIENT"
    )
    discharge_reports["START"] = pd.to_datetime(discharge_reports["START"], errors="coerce").dt.tz_localize(None)
    report = discharge_reports[discharge_reports.START == date]["generated_discharge_report"].iloc[0]
    return report


def get_anamnesis_data(
    patient_id: str, date: str, file_name: str = "anamnesis_data.csv"
) -> str:
    file_path = os.path.join(os.path.dirname(__file__), 'data', file_name)
    df = pd.read_csv(file_path)
    date = pd.to_datetime(date).tz_localize(None)
    df.date = pd.to_datetime(df.date).dt.tz_localize(None)
    filtered = df[(df.patient == patient_id) & (df.date == date) & df.generated_anamnesis.notna()]
    return filtered["generated_anamnesis"].iloc[0] if not filtered.empty else ""


def display_patient_basic_info(df: pd.DataFrame) -> None:
    df = df.iloc[:, 1:]
    st.subheader("Patient Basic Information")
    col1, col2 = st.columns(2)
    for idx, column in enumerate(df.columns):
        with col1 if idx % 2 == 0 else col2:
            st.markdown(f"- **{column.capitalize()}:** *{df[column].iloc[0]}*")


def customize_patient_date(df: pd.DataFrame, date: pd.Timestamp, column: str) -> pd.DataFrame:
    df[column] = pd.to_datetime(df[column]).dt.tz_localize(None)
    df = df.dropna(subset=[column]).drop(columns=["PATIENT"]).reset_index(drop=True)
    df = df[df[column] <= date]
    df[column] = df[column].apply(
        lambda x: (
            x.strftime("%Y-%m-%d")
            if x.hour == 0 and x.minute == 0 and x.second == 0
            else x.strftime("%Y-%m-%d %H:%M:%S")
        )
    )
    df = df.sort_values(by=column, ascending=True)

    if "STOP" in df.columns:
        df.STOP = pd.to_datetime(df.STOP).dt.tz_localize(None)
        df.STOP = df.STOP.apply(
            lambda x: (
                x.strftime("%Y-%m-%d")
                if pd.notna(x) and x.hour == 0 and x.minute == 0 and x.second == 0
                else x.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(x) else x
            )
        )
    return df


def display_patient_data(data_name: str, patient_id: str, date: str, display: bool) -> pd.DataFrame:
    date = pd.to_datetime(date).tz_localize(None)
    df = filter_csv_by_id(f"{data_name}.csv", patient_id, "PATIENT")
    df = customize_patient_date(df, date, "START") \
        if "START" in df.columns else customize_patient_date(df, date, "DATE")
    df = df.reset_index(drop=True)
    df.index = df.index + 1

    if not display:
        return df

    if df.empty:
        with st.expander(f"{data_name.replace('_',' ').capitalize()} (NA)", expanded=False):
            st.write(f"Patient has no known {data_name} until {date.date()}.")
    else:
        with st.expander(f"{data_name.replace('_',' ').capitalize()}", expanded=False):
            if data_name == "medications":
                fig = create_medicine_timeline(df)
                st.plotly_chart(fig)
            st.dataframe(df)


def get_all_data_for_timeline(patient_id: str, date: str) -> pd.DataFrame:
    df_sum = pd.DataFrame()
    for csv_data in DATA_INPUT:
        df = display_patient_data(csv_data, patient_id, date, False)

        d_col = "DESCRIPTION" if "DESCRIPTION" in df.columns else "BODYSITE_DESCRIPTION"
        df[d_col] = df[d_col].apply(lambda x: re.sub(r"\s*\(.*?\)", "", x))

        x_col = "START" if "START" in df.columns else "DATE"
        df[x_col] = pd.to_datetime(df[x_col], errors="coerce")
        df["compare_date"] = df[x_col].apply(
            lambda x: x.strftime("%Y-%m-%d") if pd.notnull(x) else None
        )
        grouped_df = (
            df.groupby("compare_date")[d_col].apply(lambda x: "; ".join(x.dropna())).reset_index()
        )
        grouped_df = grouped_df.rename(columns={d_col: "description"})
        grouped_df["source"] = csv_data.capitalize().replace("_", " ")

        df_sum = pd.concat([df_sum, grouped_df], ignore_index=True)

    df_sum = df_sum.sort_values(by=["source", "compare_date"], ascending=[True, True])
    return df_sum


def create_medicine_timeline(df: pd.DataFrame) -> go.Figure:
    unique_descriptions = df['DESCRIPTION'].unique()
    y_map = {desc: idx for idx, desc in enumerate(unique_descriptions)}

    fig = go.Figure()
    for description, group in df.groupby('DESCRIPTION'):
        for _, row in group.iterrows():
            if row['START'] == row['STOP'] or pd.isna(row['STOP']):
                fig.add_trace(go.Scatter(
                    x=[row['START']],
                    y=[y_map[description]],
                    mode='markers',
                    marker=dict(
                        size=10,
                        color=px.colors.qualitative.Set2[y_map[description] % len(px.colors.qualitative.Set2)]
                    ),
                    name=description,
                    hoverinfo='text',
                    text=f"{row['DESCRIPTION']}<br>Date: {row['START']}"
                ))
            else:
                fig.add_trace(go.Scatter(
                    x=[row['START'], row['STOP']],
                    y=[y_map[description], y_map[description]],
                    mode='lines+markers',
                    line=dict(color=px.colors.qualitative.Set2[y_map[description] % len(px.colors.qualitative.Set2)],
                              width=20),
                    marker=dict(symbol='line-ew', size=2),
                    name=description,
                    hoverinfo='text',
                    text=f"{row['DESCRIPTION']}<br>Start: {row['START']}<br>Stop: {row['STOP']}"
                ))

    shortened_labels = [desc.strip().split(" ")[0] + ' ...'
                        if len(desc.strip().split(" ")) > 1 else desc
                        for desc in unique_descriptions]

    fig.update_layout(
        title="Medications Timeline",
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Medicine",
        yaxis=dict(
            tickmode="array",
            tickvals=list(y_map.values()),
            ticktext=shortened_labels
        ),
        hovermode="closest",
        template="plotly_white",
        height=400,
        showlegend=False,
        margin=dict(l=100, r=40, t=40, b=40)
    )

    return fig


def create_timeline(df: pd.DataFrame) -> go.Figure:
    unique_sources = df["source"].unique()
    color_map = {source: color for source, color in zip(unique_sources, px.colors.qualitative.Set2)}

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["compare_date"],
            y=df["source"],
            mode="markers",
            marker=dict(size=15, color=df["source"].map(color_map), symbol="square"),
            text=df["description"].apply(lambda x: x.replace("; ", "<br>")),
            hoverinfo="text",
            name="Event",
        )
    )

    fig.update_layout(
        title="Patient Timeline",
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Patient Data",
        yaxis=dict(showticklabels=True),
        hovermode="closest",
        template="plotly_white",
        height=375,
        showlegend=False,
        margin=dict(l=40, r=40, t=40, b=40),
    )
    return fig
