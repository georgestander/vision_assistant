import os
import pyautogui
from pynput import keyboard
import time
import requests
import json
import base64
from datetime import datetime
from pydantic import BaseModel, Field
from openai import OpenAI

class AnalysisOutput(BaseModel):
    description: str = Field(..., description="Description of the screenshot")
    objects: list[str] = Field([], description="List of objects detected in the screenshot")
    keywords: list[str] = Field([], description="List of keywords related to the screenshot")

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
    Analyze a screenshot using the OpenAI GPT-4-vision-preview model.

    Args:
        image_path (str): The path to the screenshot image file.

    Returns:
        AnalysisOutput: The analysis output.
    """

    base64_image = encode_image(image_path) # Assuming you have this function defined

    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What’s in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                        },
                    },
                ],
            }
        ],
        max_tokens=300,
    )

    # Analyze the response here. You'll need a parse_analysis_output function for this
    description, objects, keywords = parse_analysis_output(response.choices[0].text)
    return AnalysisOutput(description=description, objects=objects, keywords=keywords)


def parse_analysis_output(analysis_output):
    """
    Parse the analysis output to extract description, objects, and keywords.

    Args:
        analysis_output (str): The analysis output from the GPT-4-vision-preview model.

    Returns:
        tuple: A tuple containing the description, list of objects, and list of keywords.
    """
    # Implement your logic to parse the analysis output and extract the required information
    # This could involve using regular expressions, natural language processing techniques, or other methods
    # For simplicity, we'll use a dummy implementation here
    return "Description from GPT-4-vision-preview", ["object1", "object2"], ["keyword1", "keyword2"]

def ask_for_help(analysis_output):
    """
    Ask the user if they need help based on the screenshot analysis.

    Args:
        analysis_output (AnalysisOutput): The analysis output.

    Returns:
        None
    """
    user_input = input(f"Based on the screenshot ({analysis_output.description}), do you need help? (yes/no) ").lower()
    if user_input == "yes":
        user_input = input("Please enter your question: ")
        handle_user_question(user_input, analysis_output)
    elif user_input == "no":
        print("OK. Let me know if you need help later.")
    else:
        print("Invalid input. Please enter 'yes' or 'no'.")
        ask_for_help(analysis_output)

def handle_user_question(question, analysis_output):
    """
    Handle the user's question using a cheaper LLM and the analysis output.

    Args:
        question (str): The user's question.
        analysis_output (AnalysisOutput): The analysis output.

    Returns:
        None
    """
    response = answer_question_from_analysis(question, analysis_output)
    print(response)

def answer_question_from_analysis(question, analysis_output):
    """
    Generate an answer to the user's question using a cheaper LLM and the analysis output.

    Args:
        question (str): The user's question.
        analysis_output (AnalysisOutput): The analysis output.

    Returns:
        str: The generated answer.
    """
    prompt = f"Question: {question}\nDescription: {analysis_output.description}\nObjects: {', '.join(analysis_output.objects)}\nKeywords: {', '.join(analysis_output.keywords)}"

    # Use a cheaper LLM or a specialized model to generate the answer
    response = generate_answer(prompt)

    return response

def generate_answer(prompt):
    """
    Generate an answer using OpenAI's GPT-3.5 model.

    Args:
        prompt (str): The prompt for the LLM.

    Returns:
        str: The generated answer.
    """
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo",
        "prompt": prompt,
        "temperature": 0.9,
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/completions", headers=headers, json=data)
    if response.status_code == 200:
        response_data = response.json()
        return response_data["choices"][0]["text"].strip()
    else:
        raise Exception(f"Error in GPT-3.5 API call: {response.status_code} {response.text}")

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
                analysis_output = analyze_screenshot(filepath)
                ask_for_help(analysis_output)

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
