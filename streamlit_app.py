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

draw_cards = st.button("🔁 Draw Cards")

if draw_cards:
    seed = random.random() * 143 * DAY * MONTH * YEAR
    random.seed(seed)
    selected_cards = random.sample(deck, total_cards)
    orientations = [random.choice(["upright", "reversed"]) for _ in selected_cards] if total_cards == 1 else ["upright"] * total_cards

    for i, filename in enumerate(selected_cards):
        meta = card_metadata.get(filename, {})
        title = meta.get("title", filename.replace("_", " ").title())
        orientation = orientations[i]
        meaning = meta.get(orientation, meta.get("description", ""))

        col = st.columns(total_cards)[i]
        with col:
            img_path = os.path.join(image_dir, filename)
            img = Image.open(img_path)
            if orientation == "reversed":
                img = img.rotate(180)
            st.image(img, use_column_width=True)
            st.markdown(f"### {title}{' (Reversed)' if orientation == 'reversed' else ''}")
            st.markdown(f"{meaning}")

    with st.expander("Click to view full card metadata"):
        for filename in selected_cards:
            meta = card_metadata.get(filename, {})
            st.markdown(f"**{meta.get('title', filename)}**")
            st.markdown(f"- **Upright:** {meta.get('upright', '-')}")
            st.markdown(f"- **Reversed:** {meta.get('reversed', '-')}")
            st.markdown(f"- **Zodiac:** {meta.get('zodiac', '-')}")
            st.markdown(f"- **Element:** {meta.get('element', '-')}")
            st.markdown(f"- **Yes/No:** {meta.get('yes_no', '-')}")
            st.markdown("---")
