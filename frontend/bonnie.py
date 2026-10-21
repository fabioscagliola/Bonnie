import os
import requests
import streamlit

BONNIE_URL = "http://localhost:65535"

streamlit.logo(image="assets/logo.svg", size="large")
streamlit.set_page_config(page_title="Bonnie", page_icon="assets/logo.svg", menu_items={"About": "# Bonnie \n\n A Raspberry Pi web app for displaying messages on LED matrices \n\n © 2026 Fabio Scagliola"})

streamlit.title("Bonnie")

with streamlit.form("form"):
    color = streamlit.color_picker("Color", "#FFFFFF")
    disable_scrolling = streamlit.checkbox("Disable scrolling")
    text = streamlit.text_area("Text", height=150)
    submit = streamlit.form_submit_button("Display")

if submit:
    if not text.strip():
        streamlit.error("What text?!")
    else:
        rgb = ",".join(str(x) for x in bytes.fromhex(color[1:]))

        try:
            response = requests.post(
                url=f"{BONNIE_URL}/text-scroller",
                json={
                    "text": text,
                    "disable_scrolling": disable_scrolling,
                    "color": rgb,
                },
                timeout=5,
            )
            response.raise_for_status()
            streamlit.success("Done.")

        except requests.RequestException as e:
            streamlit.error(f"Something went wrong! {e}")

if streamlit.button("Clear"):
    try:
        response = requests.post(
            url=f"{BONNIE_URL}/clear",
            timeout=5,
        )
        response.raise_for_status()
        streamlit.success("Done.")

    except requests.RequestException as e:
        streamlit.error(f"Something went wrong! {e}")

