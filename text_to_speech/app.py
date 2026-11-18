import streamlit as st

from logger import log_result
from normalizer import normalize
from tts_client import VOICES, synthesize

st.set_page_config(page_title="Epoch Reader", page_icon="🔊")
st.title("🔊 Epoch Reader")
st.caption("Cleans up tricky text before it's spoken, and logs where speech fails.")

with st.sidebar:
    voice_name = st.selectbox("Voice", list(VOICES))
    speed = st.slider("Speed (slower ← → faster)", -4.0, 4.0, 0.0, 0.5)
    st.caption("Gradium's docs call this setting padding_bonus; "
               "check which direction is faster once you have the API.")

uploaded = st.file_uploader("Upload a .txt file", type=["txt"])
default = uploaded.read().decode("utf-8") if uploaded else ""
text = st.text_area("Or paste text", value=default, height=200)

if st.button("Read it aloud", type="primary") and text.strip():
    cleaned, changes = normalize(text)
    audio, backend = synthesize(cleaned, VOICES[voice_name], speed)
    st.session_state.update(text=text, cleaned=cleaned, changes=changes,
                            audio=audio, backend=backend,
                            voice=voice_name, speed=speed)

if "audio" in st.session_state:
    s = st.session_state
    if s["backend"] == "mock":
        st.warning("Mock mode: no API key set, so this is a placeholder tone.")
    st.audio(s["audio"], format="audio/wav")
    st.download_button("Download audio", s["audio"], "speech.wav", "audio/wav")

    with st.expander(f"What was changed before speaking ({len(s['changes'])})"):
        st.dataframe(s["changes"])
        st.text_area("Cleaned text", s["cleaned"], height=120)

    st.subheader("Rate this result")
    rating = st.radio("How did it sound?", ["good", "partly wrong", "bad"], horizontal=True)
    notes = st.text_input("What went wrong (word, number, pause, voice...)?")
    if st.button("Save to feedback log"):
        log_result(original=s["text"], normalized=s["cleaned"], voice=s["voice"],
                   speed=s["speed"], backend=s["backend"], rating=rating, notes=notes)
        st.success("Saved to results_log.csv")