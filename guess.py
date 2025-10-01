# LIBRARIES --------------------------------------------------

import random # to gneraete random numbers
import tkinter as tk # for UI
from typing import Tuple # for code tidyness
from tkinter import ttk # for better UI elements
from tkinter import messagebox

# GAME ENGINE --------------------------------------------------

# One source of truth for difficulties: {name: (max_attempts, number_range)}
DIFFICULTIES: dict[str, Tuple[int, int]] = {
    "beginner": (15, 20),
    "easy":   (10, 50),
    "medium": (7, 100),
    "hard":   (5, 1000),
    "IMPOSSIBLE": (3, 10000)
}


class Game:
    def __init__(self) -> None: # Constructor
        self.score = 0  # total wins

    def start_round(self, difficulty) -> dict: # generates dict with game state and info
        self.max_attempts, number_range = DIFFICULTIES[difficulty]
        return {
            "secret": random.randint(1, number_range),
            "max_attempts": self.max_attempts,
            "number_range": number_range,
            "difficulty": difficulty,
            "won": False
        }


    def evaluate_guess(self, state: dict, guess: int) -> str: # evaluates the guess and returns feedback
        if not (1 <= guess <= state["number_range"]):
            return f"Please enter a number between 1 and {state['number_range']}."
        state["max_attempts"] -= 1
        if guess < state["secret"]:
            return "Good try, but too LOW!"
        elif guess > state["secret"]:
            return "Good try, but too HIGH!"
        else:
            state["won"] = True
            self.score += 1
            return f"🎉 Congratulations! You guessed {state['secret']} correctly!"


# ---------------------------
# UI
# ---------------------------

engine = Game() # creates game engine object
state: dict | None = None # game state variable

# CREATE TKINTER OBJECTS ------------------------------------------------
root = tk.Tk()
root.title("Number Guessing Game") # title of the window

# MAIN GAME FRAIME --------------------------------------------------

container = ttk.Frame(root, padding=16) # creates main frame / container
container.grid(sticky="nsew") # tells from to expand in all directions

# MENU USER INTERFACE ------------------------------------------------

ttk.Label(container, text="Difficulty:").grid(column=0, row=0, sticky="w") # adds a label in the first row, first column aligned left

difficulty_var = tk.StringVar(value="easy") # special variable to hold the difficulty value and update the UI when it changes

diff_combo = ttk.Combobox( # creates a dropdown menu
    container,
    textvariable=difficulty_var,
    values=["beginner", "easy", "medium", "hard", "IMPOSSIBLE"], state="readonly",width=10
)

diff_combo.grid(column=1, row=0, sticky="ew") # places the dropdown (expands east and west)

start_btn = ttk.Button(container, text="START") # creates a button to start the game
start_btn.grid(column=2, row=0, sticky="ew") # places the button (expands east and west)

info_lbl = ttk.Label(container, text="Choose a difficulty and press START!") # creates a label to show game info
info_lbl.grid(column=0, row=1, columnspan=3, pady=(10, 6), sticky="w") # places the label (expands east and west, spans 3 columns)

attempts_lbl = ttk.Label(container, text="attempts left: -") # creates a label to show attempts left
attempts_lbl.grid(column=0, row=2, columnspan=3, sticky="w") # places the label

# MAIN GAME LOOP USER INTERFACE ------------------------------------------------

ttk.Label(container, text="Your Guess:").grid(column=0, row=3, sticky="w") # creates a label for the guess input
guess_var = tk.StringVar() # special variable to hold the guess value and update the UI when it changes
guess_entry = ttk.Entry(container, textvariable=guess_var, width=12, state="disabled")
guess_entry.grid(column=1, row = 3, sticky = "w")

guess_btn = ttk.Button(container, text="GUESS", state = "disabled")
guess_btn.grid(column = 2, row = 3, padx = (6, 6))

# END OF UI CURATION ---------------------------------------------------------------

# UI HANDLING HELER FUNCTIONS ---------------------------------------------

def set_guessing_enabled(enabled: bool) -> None: # enables or disables the guessing input and button
    state_val = "normal" if enabled else "disabled"
    guess_entry.config(state=state_val) # enables or disables the guessing entry
    guess_btn.config(state=state_val) # enables or disables the guessing button

    diff_combo.config(state="readonly" if not enabled else "disabled")

def on_start() -> None: # starts a new round
    global state
    difficulty = difficulty_var.get()
    state = engine.start_round(difficulty) # starts a new round and gets the game state
    
    info_lbl.config(text=f"Guess a number between 1 and {state['number_range']}!")
    attempts_lbl.config(text=f"Attempts left: {state['max_attempts']}")
    guess_var.set("")
    set_guessing_enabled(True)
    guess_entry.focus_set() # sets focus to the guess entry

def end_round(win: bool) -> None: # ends the round and shows a message box
    set_guessing_enabled(False)
    diff_combo.config(state="readonly")
    
    # shows a message box with the result
    if win:
        messagebox.showinfo(f"You Win!", f"Correct! The secret number was {state['secret']}.")
    else:
        messagebox.showinfo("You Lose!", f"😞 Out of attempts! The secret number was {state['secret']}.")
    
    info_lbl.config(text="Choose youre difficult and press START for a new round.")

def on_guess(event=None) -> None: # handles the guess button click    

    if state is None:
        return
    raw = guess_var.get().strip()

    # input validation
    if not raw.isdigit():
        info_lbl.config("Invalid Input, Please enter a valid number.")
        return
    
    guess = int(raw)
    msg = engine.evaluate_guess(state, guess) # evaluates the guess and gets the feedback message
    info_lbl.config(text=msg) # updates the info label with the feedback message

    attempts_lbl.config(text=f"Attempts left: {state['max_attempts']}") # updates the attempts left label
    guess_var.set("") # clears the guess entry

    if state["won"]:
        end_round(win = True)
        return

    if state["max_attempts"] <= 0:
        end_round(win = False)
        return
    
# END OF UI HANDLING HELER FUNCTIONS --------------------------------------

# BIND BUTTONS TO HANDLERS ------------------------------------------------

start_btn.config(command=on_start) # binds the start button to the on_start function
guess_btn.config(command=on_guess) # binds the guess button to the on_guess function
guess_entry.bind("<Return>", on_guess)


# START THE TKINTER MAIN LOOP ------------------------------------------------
root.geometry("420x260")  # optional
root.resizable(False, False)
root.mainloop()
