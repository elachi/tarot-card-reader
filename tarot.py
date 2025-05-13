import tkinter as tk
from PIL import Image, ImageTk
import random
import os
from card_metadata import card_metadata

# Constants
DAY = 21
MONTH = 5
YEAR = 1983
CARD_WIDTH = 150
CARD_HEIGHT = 250


class TarotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tarot Card Picker")
        self.root.geometry("1000x600")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(root)
        self.canvas.grid(sticky="nsew")

        self.card_count = tk.IntVar(value=3)

        self.one_card_btn = tk.Radiobutton(root, text="Pick 1 Card", variable=self.card_count, value=1, font=("Helvetica", 10))
        self.canvas.create_window(100, 20, window=self.one_card_btn)

        self.three_cards_btn = tk.Radiobutton(root, text="Pick 3 Cards", variable=self.card_count, value=3, font=("Helvetica", 10))
        self.canvas.create_window(200, 20, window=self.three_cards_btn)

        self.pick_button = tk.Button(root, text="Pick Cards", command=self.pick_cards, font=("Helvetica", 12))
        self.canvas.create_window(320, 20, window=self.pick_button)

        self.reset_button = tk.Button(root, text="Reset Board", command=self.reset_board, font=("Helvetica", 12))
        self.canvas.create_window(470, 20, window=self.reset_button)

        self.extra_button = tk.Button(root, text="Draw Clarifier", command=self.pick_extra_card, font=("Helvetica", 12))
        self.extra_button_window = self.canvas.create_window(620, 20, window=self.extra_button)
        self.canvas.itemconfigure(self.extra_button_window, state='hidden')

        self.tarot_deck = [f for f in os.listdir("images") if f.endswith(".png")]
        self.card_image_ids = []
        self.image_refs = []
        self.extra_cards_drawn = 0

        self.root.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        self.canvas.config(width=event.width, height=event.height)

      # Reposition control buttons responsively
        canvas_width = event.width
        spacing = canvas_width // (len(self.controls) + 1)
        for i, win in enumerate(self.control_windows):
            self.canvas.coords(win, spacing * (i + 1), 20)
             

# Pick a card 
    def pick_cards(self):
        self.reset_board()
        seed = random.random() * 143 * DAY * MONTH * YEAR
        random.seed(seed)
        deck_copy = self.tarot_deck[:]
        random.shuffle(deck_copy)
        self.selected_cards = deck_copy[:self.card_count.get()]

        self.card_orientations = [random.choice(["upright", "reversed"]) for _ in self.selected_cards] if self.card_count.get() == 1 else ["upright"] * len(self.selected_cards)

        for i, filename in enumerate(self.selected_cards):
            self.root.after(i * 1000, lambda i=i, f=filename: self.show_card(i, f, orientation=self.card_orientations[i], center=self.card_count.get() == 1))

        self.canvas.itemconfigure(self.extra_button_window, state='normal')


# Pick extra card 

    def pick_extra_card(self):
        if not hasattr(self, 'selected_cards'):
            self.selected_cards = []
        remaining = list(set(self.tarot_deck) - set(self.selected_cards))
        if remaining:
            random.shuffle(remaining)
            next_card = remaining[0]
            index = len(self.selected_cards)
            self.selected_cards.append(next_card)
            self.card_orientations.append("upright")
            self.show_card(index, next_card, orientation="upright", extra=True, clarifier=True)

# Rest the board

    def reset_board(self):
        for item in self.card_image_ids:
            self.canvas.delete(item)
        self.card_image_ids.clear()
        self.image_refs.clear()
        self.extra_cards_drawn = 0
        self.selected_cards = []
        self.card_orientations = []
        self.canvas.itemconfigure(self.extra_button_window, state='hidden')

# Show card 
    def show_card(self, index, filename, orientation="upright", center=False, extra=False, clarifier=False):
        try:
            canvas_width = self.canvas.winfo_width()
            filepath = os.path.join("images", filename)
            img = Image.open(filepath)
            if orientation == "reversed":
                img = img.rotate(180)
            img = img.resize((CARD_WIDTH, CARD_HEIGHT), Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)

            if center:
                x = canvas_width // 2
            elif extra:
                base_count = len(self.selected_cards) - 1
                x = canvas_width // 2 - ((self.card_count.get() - 1) * 100) + (base_count * 200)
                self.extra_cards_drawn += 1
            else:
                total_width = (self.card_count.get() - 1) * 200
                x = canvas_width // 2 - total_width // 2 + index * 200

            img_id = self.canvas.create_image(x, 220, image=tk_img)
            self.card_image_ids.append(img_id)
            self.image_refs.append(tk_img)

            meta = card_metadata.get(filename, {})
            title = meta.get("title", os.path.splitext(filename)[0].replace("_", " ").title())
            desc = meta.get(orientation, meta.get("description", ""))

            label_title = f"Clarifier: {title}" if clarifier else title
            if orientation == "reversed":
                label_title += " (Reversed)"
            title_id = self.canvas.create_text(x, 390, text=label_title, font=("Helvetica", 14, "bold"))
            desc_id = self.canvas.create_text(x, 420, text=desc, font=("Helvetica", 12), width=180)

            self.card_image_ids.extend([title_id, desc_id])

            self.canvas.tag_bind(img_id, '<Button-1>', lambda e, f=filename: self.show_popup(f, orientation))

        except Exception as e:
            print(f"Error loading image {filename}: {e}")

# Pop up 
    def show_popup(self, filename, orientation="upright"):
        meta = card_metadata.get(filename)
        if not meta:
            return

        popup = tk.Toplevel(self.root)
        popup.title(meta.get("title", "Card Details"))
        popup.geometry("400x300")

        tk.Label(popup, text=meta.get("title", ""), font=("Helvetica", 16, "bold")).pack(pady=10)
        text = tk.Text(popup, wrap="word", font=("Helvetica", 11))
        text.pack(expand=True, fill="both", padx=10, pady=5)

        if orientation == "reversed":
            details = f"Reversed Meaning: {meta.get('reversed', '')}\n\n"
        else:
            details = f"Upright Meaning: {meta.get('upright', '')}\n\n"
        details += f"Zodiac: {meta.get('zodiac', '')}\n"
        details += f"Element: {meta.get('element', '')}\n"
        details += f"Yes/No: {meta.get('yes_no', '')}\n"

        text.insert("1.0", details)
        text.config(state="disabled")



        


if __name__ == "__main__":
    root = tk.Tk()
    app = TarotApp(root)
    root.mainloop()