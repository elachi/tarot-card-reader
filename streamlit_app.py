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

# Initialize session state
if "draw_triggered" not in st.session_state:
    st.session_state.draw_triggered = False
if "selected_cards" not in st.session_state:
    st.session_state.selected_cards = []
if "orientations" not in st.session_state:
    st.session_state.orientations = []
if "clarifier_drawn" not in st.session_state:
    st.session_state.clarifier_drawn = False
if "clarifier_card" not in st.session_state:
    st.session_state.clarifier_card = None
if "deck_pointer" not in st.session_state:
    st.session_state.deck_pointer = 0
if "shuffled_deck" not in st.session_state:
    st.session_state.shuffled_deck = []

# User selects how many cards
total_cards = st.radio("How many cards would you like to draw?", [1, 3])

# Top row: draw, reset, clarifier
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    draw_cards = st.button("🔁 Draw Cards")
if draw_cards:
    st.session_state.draw_triggered = True
with col2:
    reset_game = st.button("🔄 Reset Reading")
with col3:
    draw_clarifier = False
    if st.session_state.draw_triggered and not st.session_state.clarifier_drawn:
        draw_clarifier = st.button("🃏 Draw Clarifier Card", key=f"clarifier_button_{random.randint(0, 99999)}")

# Reset state
if reset_game:
    st.session_state.selected_cards = []
    st.session_state.orientations = []
    st.session_state.shuffled_deck = []
    st.session_state.deck_pointer = 0
    st.session_state.clarifier_drawn = False
    st.session_state.clarifier_card = None
    st.rerun()

# Draw new cards
if draw_cards:
    st.session_state.draw_triggered = True
    seed = random.random() * 143 * DAY * MONTH * YEAR
    random.seed(seed)
    deck_copy = deck[:]
    random.shuffle(deck_copy)
    st.session_state.shuffled_deck = deck_copy
    st.session_state.deck_pointer = 0
    st.session_state.selected_cards = deck_copy[:total_cards]
    st.session_state.deck_pointer += total_cards
    st.session_state.orientations = [
        "reversed" if random.random() < 0.3 else "upright"
        for _ in st.session_state.selected_cards
    ] if total_cards == 1 else ["upright"] * total_cards
    st.session_state.clarifier_drawn = False
    st.session_state.clarifier_card = None

# Define draw_clarifier default
if "draw_clarifier" not in locals():
    draw_clarifier = False

# Handle clarifier draw
if draw_clarifier:
    if st.session_state.deck_pointer < len(st.session_state.shuffled_deck):
        clarifier = st.session_state.shuffled_deck[st.session_state.deck_pointer]
        st.session_state.deck_pointer += 1
        st.session_state.clarifier_card = clarifier
        st.session_state.clarifier_drawn = True

# Show clarifier button before showing cards
# Already handled in top row

# Show reading
if st.session_state.selected_cards:
    st.subheader("Your Tarot Reading:")
    labels = ["Past", "Present", "Future"] if len(st.session_state.selected_cards) == 3 else []

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
            if labels:
                st.markdown(f"#### {labels[i]}")
            img_path = os.path.join(image_dir, filename)
            img = Image.open(img_path)
            if orientation == "reversed":
                img = img.rotate(180)
            st.image(img, width=200)
            st.markdown(f"### {title}{' (Reversed)' if orientation == 'reversed' else ''}")
            st.markdown(meaning)

# Show clarifier if available
if st.session_state.clarifier_drawn and st.session_state.clarifier_card:
    st.subheader("Clarifier Card")
    clarifier = st.session_state.clarifier_card
    meta = card_metadata.get(clarifier, {})
    title = meta.get("title", clarifier.replace("_", " ").title())
    meaning = meta.get("upright", meta.get("description", "No description available."))

    col = st.columns([1, 1, 1])[1]
    with col:
        st.image(os.path.join(image_dir, clarifier), width=200)
        st.markdown(f"### {title}")
        st.markdown(meaning)
 
# Show full metadata
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
