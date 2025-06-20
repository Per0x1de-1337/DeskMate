# DeskMate

A versatile, voice-activated desktop assistant built with Python and containerized with Docker. This application provides a conversational interface to perform various tasks using Google's Gemini Pro AI, all accessible through a clean Tkinter GUI or voice commands.


![alt text](image.png)

---

## ✨ Features

-   **Conversational AI:** Utilizes Google's Gemini 1.5 Pro model for intelligent, context-aware conversations.
-   **Containerized & Reproducible:** Runs in a Docker container for a consistent environment, eliminating "it works on my machine" issues.
-   **Dual Input Methods:** Interact via the Tkinter GUI or hands-free with voice commands.
-   **Web & Information Access:** Search Wikipedia, open Google/YouTube, or perform specific searches.
-   **System & File Operations:** Create folders and text files directly from a command.
-   **Hardware Integration:** Capture photos and record short video clips using your webcam and microphone.
-   **User-Friendly Interface:** Clean GUI with a real-time chat history and status updates.
-   **Persistent Output:** All created files (logs, photos, videos) are saved directly to your host machine.

---

## 🛠️ Core Technologies

-   **Containerization:** Docker, Docker Compose
-   **Backend:** Python 3.9+
-   **AI Engine:** Google Generative AI SDK (`google-generativeai`)
-   **GUI:** Tkinter
-   **Speech-to-Text:** `SpeechRecognition`
-   **Text-to-Speech:** `pyttsx3`
-   **Camera Control:** `OpenCV-Python`

---

## 🚀 Getting Started with Docker (Recommended)

This method is the easiest way to run the assistant, especially on **Linux**. It automatically handles all Python and system dependencies inside a container.

### Prerequisites

-   Git
-   [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)
-   A working microphone and webcam
-   **An X11-based Linux distribution** (e.g., Ubuntu, Fedora, Arch). *Running GUI apps from Docker on Windows/macOS is more complex and requires an X Server like VcXsrv or XQuartz.*

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/gemini-desktop-assistant.git
cd gemini-desktop-assistant
```

### Step 2: Get Your Google API Key

1.  Go to **[Google AI Studio](https://aistudio.google.com/)**.
2.  Click on **"Get API key"** and **"Create API key in new project"**.
3.  Copy the generated API key.

### Step 3: Create the `.env` File

Create a file named `.env` in the project's root directory. This file will securely store your API key.

```
# .env file
GOOGLE_API_KEY="YOUR_API_KEY_HERE"
```
**Important:** The `.gitignore` file is already configured to ignore `.env`, ensuring your key is not committed to Git.

### Step 4: Prepare Your Host (Linux Only)

To allow the Docker container to display its GUI on your screen, you need to grant it access to your host's X11 server. Open a terminal and run:

```bash
xhost +local:
```
> This command temporarily allows local connections to the display server. You can revert this change after closing the application by running `xhost -local:`.

### Step 5: Build and Run!

With Docker running, use Docker Compose to build the image and start the assistant with a single command:

```bash
docker-compose up --build
```

-   `--build`: This tells Docker to build the image from the `Dockerfile` the first time or if you change dependencies.
-   The GUI window should appear on your desktop. Any files created (photos, videos, logs) will be saved directly in your project folder on your host machine.

### Stopping the Assistant

-   To stop the application, press `Ctrl + C` in the terminal where Docker Compose is running.
-   To remove the container and clean up, run: `docker-compose down`.

---

## ▶️ Running the Assistant

Choose one of the following methods.

### Method 1: Using Docker (Recommended)
Follow the "Getting Started with Docker" instructions above. The final command to run the application is:
```bash
docker-compose up
```

### Method 2: Local Python Environment
<details>
  <summary>Click to expand instructions for running with a local Python setup.</summary>
  
  ### 1. Prerequisites
  - Python 3.8+
  - A virtual environment tool (`venv`)
  - System dependencies for `pyttsx3` (`espeak`) and `PyAudio` (`portaudio19-dev` on Debian/Ubuntu).

  ### 2. Set Up Virtual Environment
  ```bash
  # Create the virtual environment
  python -m venv venv

  # Activate it
  # On Windows: venv\Scripts\activate
  # On macOS/Linux: source venv/bin/activate
  ```

  ### 3. Install Dependencies
  Make sure you have a `requirements.txt` file, then run:
  ```bash
  pip install -r requirements.txt
  ```

  ### 4. Set Environment Variable
  You must set your API key as an environment variable.
  
  **On macOS/Linux:**
  ```bash
  export GOOGLE_API_KEY="YOUR_API_KEY_HERE"
  ```
  
  **On Windows (Command Prompt):**
  ```cmd
  setx GOOGLE_API_KEY "YOUR_API_KEY_HERE"
  ```
  *(You must close and reopen the terminal for the change to take effect.)*

  ### 5. Run the Application
  ```bash
  python Desktop_assistant.py
  ```
</details>

---

## 📁 Project Structure

```
.
├── Desktop_assistant.py  # Main application logic
├── Dockerfile            # Instructions to build the container image
├── docker-compose.yml    # Configures and runs the Docker service
├── .env                  # (You create this) Stores your secret API key
├── requirements.txt      # Lists Python dependencies
└── ...
```

---
## 🗣️ Available Commands

| Command                               | Action                                                         |
| ------------------------------------- | -------------------------------------------------------------- |
| `wikipedia [topic]`                   | Searches Wikipedia and reads a summary of the topic.           |
| `open google` / `open youtube`        | Opens the respective website in your browser.                  |
| `search google [query]`               | Performs a Google search for the given query.                  |
| `search youtube [query]`              | Performs a YouTube search for the given query.                 |
| `what time is it?`                    | Tells you the current time.                                    |
| `what is the date?`                   | Tells you the current date.                                    |
| `make folder [name]`                  | Creates a new folder with the specified name.                  |
| `create file [content]`               | Creates a new .txt file with the specified content.            |
| `capture photo` / `take photo`        | Captures a photo using your webcam.                            |
| `record video`                        | Records a 10-second video clip from your webcam.               |
| `tell me a joke`                      | Tells a random joke.                                           |
| `help` / `commands`                   | Displays a list of available commands.                         |
| *(any other query)*                   | The query will be sent to the Gemini AI for a response.        |

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for new features or improvements, please fork the repository and open a pull request.

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
