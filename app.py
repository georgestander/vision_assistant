import os
import pyautogui
from pynput import keyboard
import time
import requests
import json
import base64
from datetime import datetime

def encode_image(image_path):
    """
    Encode an image file as a base64 string.

    Args:
        image_path (str): The path to the image file.

    Returns:
        str: The base64-encoded image.
    """
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_image

def analyze_screenshot_and_engage_user():
    """
    Take a screenshot, analyze it using the OpenAI API, and engage in a conversation with the user about the screenshot.

    Returns:
        None
    """
    # Define the directory where you want to save the screenshot
    save_directory = "screenshots"
    os.makedirs(save_directory, exist_ok=True)

    # Prompt the user for the trigger event
    print("Press 'cmd + §' to take a screenshot and analyze it.")
    print("Waiting for trigger event...")

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
                print(f"Screenshot taken and saved at {filepath}")

                # Encode the image
                base64_image = encode_image(filepath)

                # Analyze the screenshot and engage with the user
                analyze_and_engage(base64_image)

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

def analyze_and_engage(base64_image):
    """
    Analyze the screenshot using the OpenAI API and engage in a conversation with the user.

    Args:
        base64_image (str): The base64-encoded image.

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

    continue_conversation = True

    max_messages = 5  # Adjust this value as needed

    messages = [
        {"role": "system", "content": "You are an AI assistant analyzing screenshots and engaging in conversations with users about the screenshots."},
        {"role": "user", "content": f"data:image/png;base64,{base64_image}"}
    ]

    while continue_conversation:
        payload = {
            "model": "gpt-4-vision-preview",
            "messages": messages,
            "max_tokens": 1000
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        if response.status_code == 200:
            response_data = response.json()
            if "choices" in response_data and response_data["choices"]:
                message_content = response_data["choices"][0].get("message", {}).get("content", "No description available.")
                print(message_content)

                user_input = input("Do you have any follow-up questions? (yes/no) ").lower()
                if user_input == 'yes':
                    user_question = input("Please enter your question: ")
                    messages.append({"role": "user", "content": user_question})
                    messages = messages[-max_messages:]  # Keep only the last few messages
                elif user_input == 'no':
                    print("Okay, let me know if you need help later.")
                    continue_conversation = False
                else:
                    print("Invalid input. Please try again.")
            else:
                print("No description available.")
                continue_conversation = False
        else:
            print(f"Error ({response.status_code}): {response.text}")
            continue_conversation = False

if __name__ == "__main__":
    analyze_screenshot_and_engage_user()
