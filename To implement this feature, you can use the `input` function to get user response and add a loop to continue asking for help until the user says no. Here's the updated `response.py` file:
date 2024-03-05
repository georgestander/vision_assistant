import os
import pyautogui
from pynput import keyboard
import time
import requests
import json
import base64
from datetime import datetime
import pprint

pprint.pprint(dict(os.environ))

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_screenshot(image_path):
    base64_image = encode_image(image_path)
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What’s in this image?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 100
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        if "choices" in response_data and response_data["choices"]:
            message = response_data["choices"][0].get("message", {}).get("content", "No description available.")
            print(message)
            ask_for_help(message)
        else:
            print("No description available.")
    else:
        print(f"Error ({response.status_code}): {response.text}")

def ask_for_help(image_description):
    user_input = input(f"Based on the screenshot ({image_description}), do you need help? (yes/no) ").lower()
    if user_input == "yes":
        user_input = input("Please enter your question: ")
        # TODO: Implement a function to handle user's question and provide help
        # handle_user_question(user_input)
    elif user_input == "no":
        print("OK. Let me know if you need help later.")
    else:
        print("Invalid input. Please enter 'yes' or 'no'.")
        ask_for_help(image_description)

def take_screenshot_and_analyze():
    # Define the directory where you want to save the screenshot
    save_directory = "screenshots" #create your own.
    os.makedirs(save_directory, exist_ok=True)

    # Waiting for the trigger event
    print("Waiting for trigger event: cmd + §...")

    def on_press(key):
        print("Key pressed:", key)
        print("Checking for Cmd...")  # Is it reaching this point?
        try:
            if key == keyboard.Key.cmd_l or key == keyboard.Key.cmd_r:
                on_press.is_cmd_pressed = True
        except AttributeError:
            pass

    def on_press(key):
        try:
            if key == keyboard.Key.cmd:
                on_press.cmd_pressed = True
        except AttributeError:
            pass

    def on_release(key):
        try:
            if key == keyboard.Key.cmd:
                on_press.cmd_pressed = False
            if on_press.cmd_pressed and key == keyboard.KeyCode.from_char('§'):
                # Take a screenshot
                screenshot = pyautogui.screenshot()

                # Generate a unique filename with a timestamp
                timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                filename = f"screenshot_{timestamp}.png"
                filepath = os.path.join(save_directory, filename)

                # Save the screenshot
                screenshot.save(filepath)
                print(f"Screenshot saved at {filepath}")

                # Analyze the screenshot
                analyze_screenshot(filepath)

                # Add a small delay to prevent multiple screenshots
                time.sleep(0.5)
        except AttributeError:
            pass
        if key == keyboard.Key.esc:
            # Stop listener
            return False

    on_press.cmd_pressed = False

    # Collect events until released
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

take_screenshot_and_analyze()
