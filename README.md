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

2. Change to the project directory:

   ```
   cd vision-assistant
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Set your OpenAI API key as an environment variable:

   ```
   export OPENAI_API_KEY="your_api_key_here"
   ```

## Usage

1. Run the script:

   ```
   python response.py
   ```

2. Press the keyboard shortcut (Cmd + §) to take a screenshot.

3. The script will analyze the screenshot using the OpenAI API and display the description.

4. Based on the description, the script will ask if you need help. Enter "yes" or "no".

5. If you enter "yes", the script will prompt you to enter your question. It will then use the OpenAI API to provide an answer based on the screenshot's content.

6. Press the "Esc" key to stop the script.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
