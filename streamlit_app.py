import streamlit as st
import random
from PIL import Image
import os
from card_metadata import card_metadata

# Constants
DAY = 21
MONTH = 5
YEAR = 1983

st.set_page_config(page_title="Tarot Card Reader", layout="wide")
st.title("🔮 Tarot Card Reader")

# Load images
image_dir = "images"
deck = [f for f in os.listdir(image_dir) if f.endswith(".png")]

# Initialize session state
for key, default in {
    "final_card_revealed": False,
    "final_card": None,
    "draw_triggered": False,
    "selected_cards": [],
    "orientations": [],
    "clarifier_drawn": False,
    "clarifier_card": None,
    "deck_pointer": 0,
    "shuffled_deck": []
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# User selects how many cards
total_cards = st.radio("How many cards would you like to draw?", [1, 3])

# Top row: draw, reset, clarifier, reveal last
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    draw_cards = st.button("🔁 Draw Cards")
with col2:
    reset_game = st.button("🔄 Reset Reading")
with col3:
    draw_clarifier = False
    reveal_final = False
    if st.session_state.draw_triggered and not st.session_state.clarifier_drawn:
        draw_clarifier = st.button("🃏 Draw Clarifier Card", key="clarifier_button")
    if st.session_state.draw_triggered and not st.session_state.final_card_revealed:
        reveal_final = st.button("🔒 Reveal Last Card", key="final_button")

# Reset state
if reset_game:
    for key in ["selected_cards", "orientations", "shuffled_deck", "deck_pointer",
                "clarifier_drawn", "clarifier_card", "final_card_revealed", "final_card"]:
        st.session_state[key] = [] if isinstance(st.session_state[key], list) else False
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
    st.session_state.final_card_revealed = False
    st.session_state.final_card = None

# Handle clarifier draw
if draw_clarifier:
    if st.session_state.deck_pointer < len(st.session_state.shuffled_deck):
        clarifier = st.session_state.shuffled_deck[st.session_state.deck_pointer]
        st.session_state.deck_pointer += 1
        st.session_state.selected_cards.append(clarifier)
        st.session_state.orientations.append("upright")
        st.session_state.clarifier_card = clarifier
        st.session_state.clarifier_drawn = True

# Handle final card reveal
if reveal_final:
    if st.session_state.shuffled_deck:
        final = st.session_state.shuffled_deck.pop()
        st.session_state.final_card = final
        st.session_state.final_card_revealed = True

# Show reading
if st.session_state.selected_cards:
    st.subheader("Your Tarot Reading:")
    labels = ["Past", "Present", "Future"] if total_cards == 3 else []

    num_base = 3 if total_cards == 3 else 1
    num_cards = num_base + 1 if st.session_state.clarifier_drawn else num_base
    cols = st.columns(num_cards)

    for i in range(num_cards):
        if i < len(st.session_state.selected_cards):
            filename = st.session_state.selected_cards[i]
            orientation = st.session_state.orientations[i]
            meta = card_metadata.get(filename, {})
            title = meta.get("title", filename.replace("_", " ").title())
            meaning = meta.get(orientation, meta.get("description", "No description available."))

            with cols[i]:
                if labels and i < len(labels):
                    st.markdown(f"#### {labels[i]}")
                elif st.session_state.clarifier_drawn and i == num_base:
                    st.markdown("#### Clarifier")
                img_path = os.path.join(image_dir, filename)
                img = Image.open(img_path)
                if orientation == "reversed":
                    img = img.rotate(180)
                st.image(img, width=200)
                st.markdown(f"### {title}{' (Reversed)' if orientation == 'reversed' else ''}")
                st.markdown(meaning)
        else:
            with cols[i]:
                st.empty()

# Show final card if revealed
if st.session_state.final_card_revealed and st.session_state.final_card:
    st.subheader("🔓 Final Card Revealed")
    final = st.session_state.final_card
    meta = card_metadata.get(final, {})
    title = meta.get("title", final.replace("_", " ").title())
    meaning = meta.get("upright", meta.get("description", "No description available."))

    with st.container():
        st.markdown("<div style='border: 2px solid #999; padding: 10px; border-radius: 8px; margin-top: 20px;'>", unsafe_allow_html=True)
        st.image(os.path.join(image_dir, final), width=200)
        st.markdown(f"### {title}")
        st.markdown(meaning)
        st.markdown("</div>", unsafe_allow_html=True)

# Show full metadata
with st.expander("Click to view full card metadata"):
    for filename in st.session_state.selected_cards:
        meta = card_metadata.get(filename, {})
        st.markdown(f"**{meta.get('title', filename)}**")
        st.markdown(f"- **Upright:** {meta.get('upright', meta.get('description', '-') )}")
        st.markdown(f"- **Reversed:** {meta.get('reversed', '-')}")
        st.markdown(f"- **Zodiac:** {meta.get('zodiac', '-')}")
        st.markdown(f"- **Element:** {meta.get('element', '-')}")
        st.markdown(f"- **Yes/No:** {meta.get('yes_no', '-')}")
        st.markdown("---")
