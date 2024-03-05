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

                # Analyze the screenshot with GPT-4-vision-preview
                initial_analysis = analyze_screenshot_with_gpt4(base64_image)

                print(initial_analysis)

                continue_conversation = True
                while continue_conversation:
                    user_input = input("Do you have any follow-up questions? (yes/no) ").lower()
                    if user_input == 'yes':
                        user_question = input("Please enter your question: ")
                        response = handle_user_question_with_gpt3(user_question, initial_analysis, base64_image)
                        print(response)
                    elif user_input == 'no':
                        print("Okay, let me know if you need help later.")
                        continue_conversation = False
                    else:
                        print("Invalid input. Please try again.")

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

def analyze_screenshot_with_gpt4(base64_image):
    """
    Analyze the screenshot using the OpenAI GPT-4-vision-preview model.

    Args:
        base64_image (str): The base64-encoded image.

    Returns:
        str: The analysis output.
    """
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
                "content": f"data:image/png;base64,{base64_image}"
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        if "choices" in response_data and response_data["choices"]:
            analysis_output = response_data["choices"][0].get("message", {}).get("content", "No description available.")
            return analysis_output
        else:
            return "No description available."
    else:
        print(f"Error ({response.status_code}): {response.text}")
        return f"Error ({response.status_code}): {response.text}"

def handle_user_question_with_gpt3(question, initial_analysis, base64_image):
    """
    Handle the user's question using the OpenAI GPT-3.5-turbo model.

    Args:
        question (str): The user's question.
        initial_analysis (str): The initial analysis output from GPT-4.
        base64_image (str): The base64-encoded image.

    Returns:
        str: The response to the user's question.
    """
    if can_answer_question(question, initial_analysis):
        # The initial analysis can answer the question
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        prompt = f"Based on the following analysis: '{initial_analysis}', answer the user's question: '{question}'"

        payload = {
            "model": "gpt-3.5-turbo",
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
                response_output = response_data["choices"][0].get("message", {}).get("content", "No response available.")
                return response_output
            else:
                return "No response available."
        else:
            print(f"Error ({response.status_code}): {response.text}")
            return f"Error ({response.status_code}): {response.text}"
    else:
        # The initial analysis cannot answer the question, call analyze_screenshot_with_gpt4 again
        new_analysis = analyze_screenshot_with_gpt4(base64_image, prompt=question)
        return handle_user_question_with_gpt3(question, new_analysis, base64_image)

def can_answer_question(question, analysis):
    """
    Check if the analysis output can answer the user's question.

    Args:
        question (str): The user's question.
        analysis (str): The analysis output.

    Returns:
        bool: True if the analysis can answer the question, False otherwise.
    """
    # Implement logic to check if the analysis output can answer the question
    # For example, check if certain keywords are present in the analysis
    keywords = question.lower().split()
    for keyword in keywords:
        if keyword in analysis.lower():
            return True
    return False

if __name__ == "__main__":
    analyze_screenshot_and_engage_user()
