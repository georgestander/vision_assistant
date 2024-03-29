import os
import pyautogui
from pynput import keyboard
import time
import requests
import json
import base64
from datetime import datetime
import pprint

# Print environment variables for debugging purposes
pprint.pprint(dict(os.environ))

def encode_image(image_path):
    """
    Encode an image file as a base64 string.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The base64-encoded image.
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_screenshot(image_path):
    """
    Analyze a screenshot using the OpenAI API.

    Args:
        image_path (str): The path to the screenshot image file.

    Returns:
        str: The description of the screenshot.
    """
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
                    {"type": "text", "text": "What's in this image?"},
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
            return message
        else:
            print("No description available.")
            return "No description available."
    else:
        print(f"Error ({response.status_code}): {response.text}")
        return f"Error ({response.status_code}): {response.text}"

def ask_for_help(image_description):
    """
    Ask the user if they need help based on the screenshot description.

    Args:
        image_description (str): The description of the screenshot.

    Returns:
        None
    """
    user_input = input(f"Based on the screenshot ({image_description}), do you need help? (yes/no) ").lower()
    if user_input == "yes":
        user_input = input("Please enter your question: ")
        handle_user_question(user_input, image_description)
    elif user_input == "no":
        print("OK. Let me know if you need help later.")
    else:
        print("Invalid input. Please enter 'yes' or 'no'.")
        ask_for_help(image_description)

def handle_user_question(question, image_description):
    """
    Handle the user's question using the OpenAI API.

    Args:
        question (str): The user's question.
        image_description (str): The description of the screenshot.

    Returns:
        None
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    while question.lower() != "close":
        prompt = f"Based on the following description: '{image_description}', answer the user's question: '{question}'"

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 300
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        if response.status_code == 200:
            response_data = response.json()
            if "choices" in response_data and response_data["choices"]:
                message = response_data["choices"][0].get("message", {}).get("content", "No response available.")
                print(message)
            else:
                print("No response available.")
        else:
            print(f"Error ({response.status_code}): {response.text}")

        question = input("If you have another question, type it here. Type 'close' to exit: ")

def take_screenshot_and_analyze():
    """
    Take a screenshot and analyze it using the OpenAI API.

    Returns:
        None
    """
    # Define the directory where you want to save the screenshot
    save_directory = "screenshots"
    os.makedirs(save_directory, exist_ok=True)

    # Waiting for the trigger event
    print("Waiting for trigger event: cmd + §...")

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
                image_description = analyze_screenshot(filepath)
                ask_for_help(image_description)

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

if __name__ == "__main__":
    take_screenshot_and_analyze()
