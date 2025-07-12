#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
A very simple Tkinter GUI for managing the Cloudflare WARP client.

Description:
This is a minimal script to show the WARP connection status and provide
buttons to connect or disconnect. It avoids classes and threading for simplicity.
This version includes more robust status checking based on user feedback.
"""

import tkinter as tk
from tkinter import font
import subprocess

# --- GUI Setup ---
root = tk.Tk()
root.title("WARP Control")
root.geometry("320x150") # Adjusted size for clearer messages
root.resizable(False, False)
root.tk_setPalette(background='#f0f0f0')

# --- Fonts ---
status_font = font.Font(family="Helvetica", size=14, weight='bold')
button_font = font.Font(family="Helvetica", size=10)
message_font = font.Font(family="Helvetica", size=10)

# --- UI Elements ---
status_frame = tk.Frame(root, pady=10, bg='#f0f0f0')
status_frame.pack()

tk.Label(
    status_frame,
    text="Status:",
    font=button_font,
    bg='#f0f0f0'
).pack(side=tk.LEFT, padx=(0, 5))

status_text_label = tk.Label(
    status_frame,
    text="Checking...",
    font=status_font,
    fg="orange",
    bg='#f0f0f0'
)
status_text_label.pack(side=tk.LEFT)

button_frame = tk.Frame(root, pady=10, bg='#f0f0f0')
button_frame.pack()

def connect_warp():
    """Handles the connect button action."""
    status_text_label.config(text="Connecting...", fg="orange")
    root.update_idletasks() # Force GUI update
    try:
        # Use --accept-tos to handle first-time connection prompts
        subprocess.run(['warp-cli', '--accept-tos', 'connect'], capture_output=True, check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to connect. Command output:\n{e.stdout}\n{e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred during connect: {e}")
    check_status() # Immediately re-check status

def disconnect_warp():
    """Handles the disconnect button action."""
    status_text_label.config(text="Disconnecting...", fg="orange")
    root.update_idletasks() # Force GUI update
    try:
        subprocess.run(['warp-cli', 'disconnect'], capture_output=True, check=True, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to disconnect. Command output:\n{e.stdout}\n{e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred during disconnect: {e}")
    check_status() # Immediately re-check status

connect_button = tk.Button(
    button_frame,
    text="Connect",
    font=button_font,
    command=connect_warp,
    width=12
)
connect_button.pack(pady=4)

disconnect_button = tk.Button(
    button_frame,
    text="Disconnect",
    font=button_font,
    command=disconnect_warp,
    width=12
)
disconnect_button.pack(pady=4)

def check_status():
    """Checks the warp-cli status and updates the GUI."""
    command_output = "" # Variable to store output for debugging
    try:
        # CORRECTED: Removed capture_output=True and used stdout/stderr arguments
        # to correctly capture all output from the command without conflict.
        result = subprocess.run(
            ['warp-cli', 'status'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False
        )
        command_output = result.stdout.strip() if result.stdout else ""
        output = command_output.lower()

        # Using more specific phrases based on user feedback
        if "status update: connected" in output:
            status_text_label.config(text="Connected", fg="#2ca02c") # Green
            connect_button.config(state=tk.DISABLED)
            disconnect_button.config(state=tk.NORMAL)
        elif "status update: disconnected" in output or "disabled" in output:
            status_text_label.config(text="Disconnected", fg="#d62728") # Red
            connect_button.config(state=tk.NORMAL)
            disconnect_button.config(state=tk.DISABLED)
        elif "register" in output:
            status_text_label.config(text="Run: 'warp-cli registration new'", fg="blue", font=message_font)
            connect_button.config(state=tk.DISABLED)
            disconnect_button.config(state=tk.DISABLED)
        else:
            # If the status is none of the above, it's unknown.
            status_text_label.config(text="Unknown", fg="gray")
            connect_button.config(state=tk.DISABLED)
            disconnect_button.config(state=tk.DISABLED)
            if command_output:
                print("--- UNKNOWN WARP-CLI STATUS ---")
                print("The script received this output:")
                print(command_output)
                print("---------------------------------")


    except FileNotFoundError:
        status_text_label.config(text="warp-cli not found", fg="red", font=message_font)
        connect_button.config(state=tk.DISABLED)
        disconnect_button.config(state=tk.DISABLED)
    except Exception as e:
        # Improved error logging
        print("--- SCRIPT ERROR ---")
        print(f"An exception occurred in check_status: {e}")
        if command_output:
            print("The command that may have caused the error produced this output:")
            print(command_output)
        print("--------------------")

        status_text_label.config(text="Error", fg="red")
        connect_button.config(state=tk.DISABLED)
        disconnect_button.config(state=tk.DISABLED)

    # Schedule this function to run again after 5 seconds
    root.after(5000, check_status)

# --- Start the Application ---
check_status() # Initial check
root.mainloop()
