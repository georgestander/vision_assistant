# Vision Assistant

Vision Assistant is a Python script that allows users to take screenshots, analyze them using the OpenAI API, and ask for help based on the screenshot's content.

## Features

- Take screenshots using a keyboard shortcut (Cmd + §)
- Analyze screenshots using the OpenAI API (gpt-4-vision-preview model)
- Ask the user if they need help based on the screenshot's description
- Handle user questions using the OpenAI API (gpt-4-vision-preview model)

## Prerequisites

- Python 3.x
- OpenAI API key (set as an environment variable named `OPENAI_API_KEY`)

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/vision-assistant.git
   ```

2. Navigate to the project directory:

   ```
   cd vision-assistant
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```
   Replace `your_api_key_here` with your actual OpenAI API key.

## Usage

1. Run the `app.py` script:

   ```
   python app.py
   ```

2. The script will start and wait for the trigger event (Cmd + §).

3. Press Cmd + § to take a screenshot. The screenshot will be saved in the `screenshots` directory with a unique filename based on the current timestamp.

4. The script will analyze the screenshot using the OpenAI API and display the description of the screenshot.

5. The script will prompt you to enter whether you need help based on the screenshot description. Enter 'yes' or 'no'.

6. If you enter 'yes', the script will prompt you to enter your question. Type your question and press Enter.

7. The script will use the OpenAI API to generate a response to your question based on the screenshot description and display the response.

8. If you enter 'no', the script will acknowledge and wait for further assistance.

9. To exit the script, press the 'Esc' key.

## Customization

- You can modify the keyboard shortcut for taking screenshots by changing the key combination in the `on_release` function of the `take_screenshot_and_analyze` function in `app.py`.

- The directory where screenshots are saved can be changed by modifying the `save_directory` variable in the `take_screenshot_and_analyze` function.

- The OpenAI API model used for analyzing screenshots and generating responses can be changed by modifying the `model` parameter in the `payload` dictionaries of the `analyze_screenshot` and `handle_user_question` functions.

## Troubleshooting

- If you encounter any issues related to the OpenAI API, ensure that your API key is set correctly as an environment variable.

- If the script fails to take screenshots, make sure you have the necessary permissions and that the `screenshots` directory exists or can be created.

- If you face any dependency-related issues, ensure that you have installed all the required packages listed in the `requirements.txt` file.
