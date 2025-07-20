# VoiceSync Gmail Assistant

VoiceSync Gmail Assistant is a Python-based desktop application that allows users to manage their Gmail emails using voice commands, keyboard inputs, or a graphical user interface (GUI). Built with the Google Gmail API, spaCy for natural language processing (NLP), and CustomTkinter for the GUI, this app lets you read, send, delete, archive, or move emails effortlessly. Whether you're hands-free with voice control or prefer clicking buttons, VoiceSync makes email management simple and intuitive.

## Features

- **Voice and Keyboard Control**: Use voice commands (e.g., "read email," "send email") or type commands to interact with Gmail.
- **Email Operations**:
  - **Read Emails**: Fetch emails from labels like Inbox, Spam, Social, or Promotions.
  - **Send Emails**: Compose and send emails with formatted text (bold, italic, etc.).
  - **Delete Emails**: Move emails to Trash or delete them permanently with confirmation.
  - **Archive/Move Emails**: Organize emails by moving them to custom labels or archiving them.
- **Graphical User Interface (GUI)**: A user-friendly interface with buttons (Start, Stop, Quit) and a real-time email count graph for labels like Inbox, Spam, and Social.
- **Natural Language Processing**: Uses spaCy to understand varied commands (e.g., "check email," "compose message").
- **Secure Authentication**: Integrates Google OAuth2 for safe access to your Gmail account.
- **Reliable Design**: Includes retry limits, error handling, and thread-safe GUI updates for a smooth experience.

## Technologies Used

- **Python Libraries**: `googleapiclient`, `spacy`, `speech_recognition`, `pyttsx3`, `customtkinter`, `matplotlib`, `bs4`, `inflect`
- **Google Gmail API**: For email operations (read, send, delete, move).
- **spaCy**: For processing voice and text commands.
- **CustomTkinter**: For the GUI with buttons and email visualizations.
- **Matplotlib**: For displaying email count graphs.

## Setup Instructions

Follow these steps to set up and run VoiceSync Gmail Assistant on your computer.

### Prerequisites
- Python 3.8 or higher
- A Gmail account with Google API credentials (see below)
- A microphone for voice input (optional for keyboard/GUI use)

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/voicesync-gmail-assistant.git
   cd voicesync-gmail-assistant
   ```

2. **Install Dependencies**:
   Create a virtual environment and install required packages:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
   The `requirements.txt` should include:
   ```
   google-api-python-client
   google-auth-httplib2
   google-auth-oauthlib
   spacy
   speechrecognition
   pyttsx3
   customtkinter
   matplotlib
   beautifulsoup4
   inflect
   ```

3. **Set Up Google Gmail API**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a project and enable the **Gmail API**.
   - Create OAuth 2.0 credentials (select “Desktop app”).
   - Download the credentials as `credentials.json` and place it in the project’s root folder.
   - Note: Do **not** share `credentials.json` or `token.pickle` (generated after authentication).

4. **Download spaCy Model**:
   Install the spaCy English model for NLP:
   ```bash
   python -m spacy download en_core_web_sm
   ```

### Running the App
- **GUI Mode**: Start the graphical interface (recommended):
  ```bash
  python ui.py
  ```
  - Click “Start Assistant” to begin, use voice/keyboard commands, or click buttons.
  - View email counts with the “Show Email Count Graph” button.
- **Command-Line Mode**: Use voice or keyboard without the GUI:
  ```bash
  python main.py
  ```
  - Say “Hey Assistant” or press Enter to start, then give commands like “read email” or “send email.”

## Usage

1. **Start the Assistant**:
   - In GUI mode, click “Start Assistant” or say “Hey Assistant.”
   - In command-line mode, press Enter or say “Hey Assistant.”

2. **Available Commands**:
   - **Read Emails**: “read email” or “check email” → Choose a label (e.g., “inbox,” “social”).
   - **Send Emails**: “send email” → Provide recipient, subject, and message.
   - **Delete Emails**: “delete email” → Choose “trash” or “permanent,” then specify the email.
   - **Archive/Move Emails**: “archive email” or “move email” → Select a label and email.
   - **Exit**: “exit” or “stop” to quit the assistant.
   - **Back**: “back” to return to the start (GUI/command-line).

3. **GUI Features**:
   - View your last command and system logs in the GUI.
   - Click “Show Email Count Graph” to see a bar chart of email counts by label (e.g., Inbox, Spam).
   - Toggle between Dark and Light themes for comfort.

4. **Example**:
   - Say: “send email”
   - Assistant: “Who do you want to send the email to?”
   - Say: “friend@gmail.com”
   - Assistant: “What is the subject?”
   - Say: “Meeting tomorrow”
   - Assistant: “What is the message?”
   - Say: “Let’s meet at 10 AM.”
   - Assistant: Sends the email and confirms.

## Project Structure

- **`main.py`**: Main logic for processing voice/keyboard commands and coordinating email operations.
- **`ui.py`**: Graphical interface with buttons, logs, and email count visualization.
- **`email_sender.py`**: Handles sending emails with formatted text.
- **`email_anylabel_reader.py`**: Reads emails from specific Gmail labels.
- **`email_reader_specific.py`**: Searches and reads emails by keywords.
- **`email_delete.py`**: Moves emails to Trash (soft delete).
- **`permanenta_delete.py`**: Permanently deletes emails.
- **`email_archive_move_any.py`**: Archives or moves emails to labels.
- **`utils/gmail_auth.py`**: Manages OAuth2 authentication for Gmail API.
- **`speech_processing/voice_assistant.py`**: Handles voice input (Whisper) and output (pyttsx3).
- **`.gitignore`**: Excludes sensitive files like `token.pickle` and `credentials.json`.

## Contributing

We welcome contributions! To contribute:
1. Fork the repository.
2. Create a branch: `git checkout -b feature-name`.
3. Make changes and commit: `git commit -m "Add feature-name"`.
4. Push to your fork: `git push origin feature-name`.
5. Open a Pull Request on GitHub.

Please ensure your code follows the project’s style (PEP 8) and includes error handling.

## Security Notes
- **Do not share** `credentials.json` or `token.pickle`, as they contain sensitive authentication data.
- The `.gitignore` file ensures these files are not uploaded to GitHub.

## Future Improvements
- Add email reply functionality.
- Support more complex voice commands (e.g., “read unread emails from John”).
- Enhance GUI with more interactive features (e.g., email preview panel).
- Add unit tests for reliability.

## Acknowledgments
- Built with inspiration from voice assistant and email automation projects.
- Thanks to Google Gmail API, spaCy, and CustomTkinter communities for their robust tools.

For issues or suggestions, open a GitHub issue or contact [your email or GitHub profile].