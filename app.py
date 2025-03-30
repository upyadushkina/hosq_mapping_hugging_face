# app.py — Gradio версия
import gradio as gr
import pandas as pd
from pyvis.network import Network
import tempfile
import os
from pathlib import Path

# Загружаем данные
df = pd.read_csv("Etudes Lab 1 artistis.csv").fillna("")
df["professional field"] = df["professional field"].astype(str)
df["role"] = df["role"].astype(str)

def convert_drive_url(url):
    if "drive.google.com" in url and "/file/d/" in url:
        try:
            file_id = url.split("/file/d/")[1].split("/")[0]
            return f"https://drive.google.com/uc?export=view&id={file_id}"
        except IndexError:
            return url
    return url

# Граф построения
def build_graph(name_filter):
    net = Network(height="600px", width="100%", bgcolor="#262123", font_color="#E8DED3")

    NODE_NAME_COLOR = "#4C4646"
    NODE_CITY_COLOR = "#D3DAE8"
    NODE_FIELD_COLOR = "#EEC0E7"
    NODE_ROLE_COLOR = "#F4C07C"

    filtered_df = df.copy()
    if name_filter:
        filtered_df = filtered_df[filtered_df["name"] == name_filter]

    for _, row in filtered_df.iterrows():
        name = row["name"].strip()
        city = row["city"].strip()
        country = row["country and city"].strip()
        location = country
        fields = [f.strip() for f in row["professional field"].split(",") if f.strip()]
        roles = [r.strip() for r in row["role"].split(",") if r.strip()]
        telegram = row["telegram nickname"].strip()
        email = row["email"].strip()
        photo = convert_drive_url(row["photo"].strip()) if row["photo"].strip() else ""

        info = name
        if telegram:
            info += f"\nTelegram: {telegram}"
        if email:
            info += f"\nEmail: {email}"

        net.add_node(name, label=name, title=info, color=NODE_NAME_COLOR, shape="dot", size=20)
        if location:
            net.add_node(location, label=location, title=location, color=NODE_CITY_COLOR, shape="dot", size=15)
            net.add_edge(name, location)
        for field in fields:
            net.add_node(field, label=field, title=field, color=NODE_FIELD_COLOR, shape="dot", size=15)
            net.add_edge(name, field)
        for role in roles:
            net.add_node(role, label=role, title=role, color=NODE_ROLE_COLOR, shape="dot", size=15)
            net.add_edge(name, role)

    # Сохраняем граф
    tmp_dir = tempfile.gettempdir()
    tmp_path = os.path.join(tmp_dir, "graph.html")
    net.show_buttons(filter_=['physics'])
    net.save_graph(tmp_path)

    with open(tmp_path, "r", encoding="utf-8") as f:
        html = f.read()
    return html

# Получаем список участников
names = sorted(df["name"].dropna().unique().tolist())

# Интерфейс Gradio
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎨 HOSQ Artists Network")
    name_select = gr.Dropdown(choices=[""] + names, label="Choose an artist")
    graph_output = gr.HTML()

    name_select.change(fn=build_graph, inputs=name_select, outputs=graph_output)
    graph_output.value = build_graph("")

demo.launch()
