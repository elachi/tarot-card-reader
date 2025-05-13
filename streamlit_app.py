import streamlit as st
import random
from PIL import Image
import os
from card_metadata import card_metadata

# Constants
DAY = 21
MONTH = 5
YEAR = 1983

st.set_page_config(page_title="Tarot Card Reader", layout="centered")
st.title("🔮 Tarot Card Reader")

# Load images
image_dir = "images"
deck = [f for f in os.listdir(image_dir) if f.endswith(".png")]

total_cards = st.radio("How many cards would you like to draw?", [1, 3])

if "selected_cards" not in st.session_state:
    st.session_state.selected_cards = []
    st.session_state.orientations = []

draw_cards = st.button("🔁 Draw Cards")
if draw_cards:
    seed = random.random() * 143 * DAY * MONTH * YEAR
    random.seed(seed)
    st.session_state.selected_cards = random.sample(deck, total_cards)
    st.session_state.orientations = [random.choice(["upright", "reversed"]) for _ in st.session_state.selected_cards] if total_cards == 1 else ["upright"] * total_cards

if st.session_state.selected_cards:
    st.subheader("Your Tarot Reading:")
    cols = st.columns(len(st.session_state.selected_cards))
    if len(st.session_state.selected_cards) == 1:
    cols = [st.columns([1, 2, 1])[1]]
elif len(st.session_state.selected_cards) == 3:
    cols = st.columns(3)
else:
    cols = [st.container() for _ in st.session_state.selected_cards]

for i, (filename, orientation) in enumerate(zip(st.session_state.selected_cards, st.session_state.orientations)):
    meta = card_metadata.get(filename, {})
    title = meta.get("title", filename.replace("_", " ").title())
    meaning = meta.get(orientation, meta.get("description", "No description available."))

    with cols[i]:
            img_path = os.path.join(image_dir, filename)
            img = Image.open(img_path)
            if orientation == "reversed":
                img = img.rotate(180)
            st.image(img, width=200)
            st.markdown(f"### {title}{' (Reversed)' if orientation == 'reversed' else ''}")
            st.markdown(meaning)

    if len(st.session_state.selected_cards) < 4:
        if st.button("🃏 Draw Clarifier Card"):
            remaining = list(set(deck) - set(st.session_state.selected_cards))
            if remaining:
                random.shuffle(remaining)
                clarifier = remaining[0]
                st.session_state.selected_cards.append(clarifier)
                st.session_state.orientations.append("upright")
                st.experimental_rerun()

    with st.expander("Click to view full card metadata"):
        for filename in st.session_state.selected_cards:
            meta = card_metadata.get(filename, {})
            st.markdown(f"**{meta.get('title', filename)}**")
            st.markdown(f"- **Upright:** {meta.get('upright', meta.get('description', '-'))}")
            st.markdown(f"- **Reversed:** {meta.get('reversed', '-')}")
            st.markdown(f"- **Zodiac:** {meta.get('zodiac', '-')}")
            st.markdown(f"- **Element:** {meta.get('element', '-')}")
            st.markdown(f"- **Yes/No:** {meta.get('yes_no', '-')}")
            st.markdown("---")
