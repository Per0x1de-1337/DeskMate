import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import google.generativeai as genai 
import cv2
import threading
import logging
from typing import Optional
import json
import random

class DesktopAssistant:
    def __init__(self):
        """
        Initializes the Desktop Assistant application.
        """
        self.setup_logging()
        self.setup_tts()
        self.setup_gemini_native()  
        self.setup_gui()
        self.is_recording = False

    def setup_logging(self):
        """Configure logging for better debugging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('assistant.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def setup_tts(self):
        """Initialize text-to-speech with error handling."""
        try:
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            if voices:
                english_voice = next(
                    (voice for voice in voices if "english" in voice.name.lower()),
                    voices[0]
                )
                self.engine.setProperty('voice', english_voice.id)
                self.engine.setProperty('rate', 150)  
                self.engine.setProperty('volume', 0.9)
            self.logger.info("TTS initialized successfully")
        except Exception as e:
            self.logger.error(f"TTS initialization failed: {e}")
            self.engine = None

    def setup_gemini_native(self):
        """
        Setup Google Gemini using the native SDK.
        Reads the API key from the environment variable 'GOOGLE_API_KEY'.
        """
        try:
            api_key = "AIzaSyCzVeP0cUv0cUuNfcfgAEK07eJI1tvJCoQ"
            if not api_key:
                self.logger.error("GOOGLE_API_KEY environment variable not set. AI features will be disabled.")
                messagebox.showerror("API Key Error", "GOOGLE_API_KEY not found. Please set the environment variable.")
                self.model = None
                return

            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.logger.info("Google Gemini native client configured successfully.")
        except Exception as e:
            self.logger.error(f"Failed to configure Gemini AI: {e}")
            self.model = None

    def setup_gui(self):
        """Create the main graphical user interface for the assistant."""
        self.root = tk.Tk()
        self.root.title('Desktop Assistant - Gemini Powered')
        self.root.geometry('900x700')
        self.root.configure(bg='#2c3e50')
        self.root.resizable(True, True)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=6, relief="flat", background="#3498db", foreground="white", font=('Arial', 10, 'bold'))
        style.map("TButton", background=[('active', '#2980b9')])
        style.configure("TFrame", background='#2c3e50')
        style.configure("TLabel", background='#2c3e50', foreground='white')
        style.configure("TEntry", fieldbackground="#34495e", foreground="white", insertbackground="white")

        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        title_label = ttk.Label(main_frame, text="🤖 Desktop Assistant", font=('Arial', 20, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))

        chat_frame = ttk.Frame(main_frame)
        chat_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, state=tk.DISABLED, bg='#34495e',
            fg='white', font=('Consolas', 11), height=25, relief=tk.FLAT, borderwidth=2
        )
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.chat_display.tag_configure("user", foreground="#3498db", font=('Consolas', 11, 'bold'))
        self.chat_display.tag_configure("assistant", foreground="#2ecc71", font=('Consolas', 11, 'bold'))
        self.chat_display.tag_configure("system", foreground="#f39c12", font=('Consolas', 11, 'italic'))
        self.chat_display.tag_configure("error", foreground="#e74c3c", font=('Consolas', 11, 'bold'))

        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)

        self.message_var = tk.StringVar()
        self.message_var.trace('w', self.validate_input)
        self.message_entry = ttk.Entry(
            input_frame, textvariable=self.message_var, font=('Arial', 12),
            validate='key', validatecommand=(self.root.register(lambda v: len(v) <= 500), '%P')
        )
        self.message_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))

        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=0, column=1)

        self.send_button = ttk.Button(button_frame, text='Send', command=self.send_message, state=tk.DISABLED)
        self.send_button.grid(row=0, column=0, padx=(0, 5))
        self.mic_button = ttk.Button(button_frame, text='Voice', command=self.activate_microphone_threaded)
        self.mic_button.grid(row=0, column=1, padx=(0, 5))
        self.clear_button = ttk.Button(button_frame, text='Clear', command=self.clear_chat)
        self.clear_button.grid(row=0, column=2)

        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor='w', padding=5)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        self.message_entry.bind('<Return>', self.send_message)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.message_entry.focus()

    def validate_input(self, *args):
        """Enable or disable the send button based on input."""
        message = self.message_var.get().strip()
        self.send_button.config(state=tk.NORMAL if message else tk.DISABLED)

    def clear_chat(self):
        """Clears the chat display."""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.update_chat("Chat cleared", "system")

    def take_command(self) -> Optional[str]:
        """Listens for a voice command and returns it as text."""
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 400
        recognizer.pause_threshold = 0.8

        try:
            with sr.Microphone() as source:
                self.update_status("🎤 Listening...")
                self.update_chat("🎤 Listening...", "system")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)

            self.update_status("Processing speech...")
            self.update_chat("Processing speech...", "system")
            query = recognizer.recognize_google(audio, language='en-US')
            self.logger.info(f"Recognized: {query}")
            return query.lower()

        except sr.UnknownValueError:
            self.speak("Sorry, I didn't understand that. Please try again.")
            return None
        except sr.WaitTimeoutError:
            self.speak("No speech detected. Please try again.")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition service error: {e}")
            self.speak("The speech recognition service is unavailable.")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in speech recognition: {e}")
            return None
        finally:
            self.update_status("Ready")

    def activate_microphone_threaded(self):
        """Handles microphone activation in a separate thread to keep the GUI responsive."""
        self.mic_button.config(state=tk.DISABLED, text="Recording...")
        thread = threading.Thread(target=self._microphone_worker)
        thread.daemon = True
        thread.start()

    def _microphone_worker(self):
        """Worker function for voice command processing."""
        try:
            query = self.take_command()
            if query:
                self.root.after(0, lambda: self.update_chat(f"👤 You: {query}", "user"))
                self.root.after(0, lambda: self.process_query(query))
        finally:
            self.root.after(0, lambda: self.mic_button.config(state=tk.NORMAL, text="🎤 Voice"))

    def process_query(self, query: str):
        """Processes the user's text query and routes it to the correct function."""
        query = query.lower().strip()
        self.update_status("Processing...")

        try:
            if 'wikipedia' in query: self.search_wikipedia(query)
            elif 'open youtube' in query: self.open_youtube()
            elif 'open google' in query: self.open_google()
            elif 'search youtube' in query or 'youtube search' in query: self.search_youtube(query)
            elif 'search google' in query or 'google search' in query: self.search_google(query)
            elif 'time' in query: self.tell_time()
            elif 'date' in query: self.tell_date()
            elif 'make folder' in query or 'create folder' in query: self.create_folder(query)
            elif 'record video' in query: self.record_video_threaded()
            elif 'capture photo' in query or 'take photo' in query: self.capture_photo()
            elif 'create file' in query: self.create_file(query)
            elif 'weather' in query: self.get_weather()
            elif 'joke' in query: self.tell_joke()
            elif 'help' in query or 'commands' in query: self.show_help()
            else:
                self.handle_ai_query(query)

        except Exception as e:
            self.logger.error(f"Error processing query '{query}': {e}")
            self.speak("Sorry, I encountered an error processing your request.")
        finally:
            self.update_status("Ready")

    def handle_ai_query(self, query: str):
        """Handle general AI queries using Google's native Gemini SDK."""
        try:
            if not self.model:
                self.speak("AI functionality is not configured. Please check your Google API key.")
                return

            self.update_status("Thinking with Gemini...")
            self.speak("Let me think about that...")

            generation_config = genai.types.GenerationConfig(
                max_output_tokens=250, temperature=0.7, top_p=0.9, top_k=40
            )

            enhanced_query = (f"You are a helpful and friendly desktop assistant. "
                              f"Keep your responses concise and directly answer the user's question.\n\n"
                              f"User query: {query}\n\nAssistant response:")

            response = self.model.generate_content(
                enhanced_query,
                generation_config=generation_config
            )

            if not response.parts:
                self.logger.warning(f"Gemini response blocked. Prompt feedback: {response.prompt_feedback}")
                self.speak("Sorry, I can't respond to that query due to safety guidelines.")
                return

            ai_response = response.text.strip()
            self.speak(ai_response)

        except Exception as e:
            error_msg = str(e).lower()
            self.logger.error(f"Gemini API error: {e}")
            if "api key" in error_msg or "authentication" in error_msg:
                self.speak("Google API authentication failed. Please check your API key.")
            elif "quota" in error_msg or "rate limit" in error_msg:
                self.speak("Google API quota exceeded. Please try again later.")
            elif "resource has been exhausted" in error_msg:
                self.speak("The AI service is currently busy. Please try again in a moment.")
            else:
                self.speak("Sorry, I couldn't process that with the AI right now.")

    def search_wikipedia(self, query: str):
        """Searches Wikipedia for a given term and speaks a summary."""
        try:
            search_term = query.replace("wikipedia", "").replace("search", "").strip()
            if not search_term:
                self.speak("What would you like me to search for on Wikipedia?")
                return

            self.speak(f"Searching Wikipedia for {search_term}...")
            self.update_status("Searching Wikipedia...")
            results = wikipedia.summary(search_term, sentences=3, auto_suggest=True)
            response = f"According to Wikipedia: {results}"
            self.speak(response)

        except wikipedia.exceptions.DisambiguationError as e:
            self.speak(f"Multiple results found. For example: {e.options[0]}. Please be more specific.")
        except wikipedia.exceptions.PageError:
            self.speak(f"Sorry, I couldn't find a Wikipedia page for {search_term}.")
        except Exception as e:
            self.logger.error(f"Wikipedia search error: {e}")
            self.speak("Sorry, I encountered an error while searching Wikipedia.")

    def open_youtube(self):
        """Opens YouTube in the default web browser."""
        webbrowser.open("https://youtube.com")
        self.speak("Opening YouTube.")

    def open_google(self):
        """Opens Google in the default web browser."""
        webbrowser.open("https://google.com")
        self.speak("Opening Google.")

    def search_youtube(self, query: str):
        """Performs a search on YouTube."""
        search_term = query.replace("search youtube", "").replace("youtube search", "").replace("on youtube", "").strip()
        if not search_term:
            self.speak("What should I search for on YouTube?")
            return
        youtube_url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
        webbrowser.open(youtube_url)
        self.speak(f"Searching YouTube for {search_term}.")

    def search_google(self, query: str):
        """Performs a search on Google."""
        search_term = query.replace("search google", "").replace("google search", "").replace("on google", "").strip()
        if not search_term:
            self.speak("What should I search for on Google?")
            return
        google_url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
        webbrowser.open(google_url)
        self.speak(f"Searching Google for {search_term}.")

    def tell_time(self):
        """Tells the current time."""
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        self.speak(f"The current time is {current_time}.")

    def tell_date(self):
        """Tells the current date."""
        current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
        self.speak(f"Today is {current_date}.")

    def create_folder(self, query: str):
        """Creates a new folder on the desktop."""
        folder_name = query.replace("make folder", "").replace("create folder", "").strip()
        if not folder_name:
            self.speak("What should I name the folder?")
            return
        
        folder_name = "".join(c for c in folder_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        desktop_path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
        folder_path = os.path.join(desktop_path, folder_name)

        if os.path.exists(folder_path):
            self.speak(f"A folder named '{folder_name}' already exists on your desktop.")
        else:
            os.makedirs(folder_path)
            self.speak(f"Folder '{folder_name}' created on your desktop.")

    def record_video_threaded(self):
        """Starts video recording in a separate thread."""
        if self.is_recording:
            self.speak("A recording is already in progress.")
            return
        thread = threading.Thread(target=self.record_video)
        thread.daemon = True
        thread.start()

    def record_video(self):
        """Records a 10-second video from the default camera."""
        try:
            self.is_recording = True
            self.speak("Starting video recording for 10 seconds. Press Q in the video window to stop early.")
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.speak("Cannot access the camera.")
                return

            width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recorded_video_{timestamp}.avi"
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(filename, fourcc, 20.0, (width, height))
            
            start_time = datetime.datetime.now()
            while (datetime.datetime.now() - start_time).total_seconds() < 10:
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
                    cv2.imshow('Recording... (Press Q to stop)', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    break
            
            self.speak(f"Video recorded successfully and saved as {filename}")

        except Exception as e:
            self.logger.error(f"Video recording error: {e}")
            self.speak("Sorry, I couldn't record the video.")
        finally:
            if 'cap' in locals() and cap.isOpened(): cap.release()
            if 'out' in locals(): out.release()
            cv2.destroyAllWindows()
            self.is_recording = False

    def capture_photo(self):
        """Captures a single photo from the default camera."""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.speak("Cannot access the camera.")
                return

            self.speak("Say cheese!")
            ret, frame = cap.read()
            if ret:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"captured_photo_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                self.speak(f"Photo captured and saved as {filename}")
            else:
                self.speak("Failed to capture photo.")
            cap.release()
        except Exception as e:
            self.logger.error(f"Photo capture error: {e}")
            self.speak("Sorry, I couldn't capture the photo.")

    def create_file(self, query: str):
        """Creates a text file with specified content."""
        content = query.replace("create file", "").strip()
        if not content:
            content = "This file was created by the Desktop Assistant."

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"assistant_file_{timestamp}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        self.speak(f"File '{filename}' created successfully.")

    def get_weather(self):
        """Informs the user about the lack of a weather service."""
        self.speak("I am not connected to a live weather service at the moment. You can ask me to search Google for the weather in your city.")

    def tell_joke(self):
        """Tells a random joke."""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "I told my computer I needed a break, and now it won’t stop sending me Kit-Kat ads."
        ]
        self.speak(random.choice(jokes))

    def show_help(self):
        """Displays a list of available commands."""
        help_text = """
        Here are some commands you can use:
        
        • 'Wikipedia [topic]' -> Search Wikipedia.
        • 'Open YouTube/Google' -> Open websites.
        • 'Search YouTube/Google [query]' -> Search on sites.
        • 'What time is it?' / 'What is the date?'
        • 'Make folder [name]' -> Create a folder.
        • 'Record video' / 'Capture photo'
        • 'Create file [content]' -> Create a text file.
        • 'Tell me a joke'
        • Ask anything else for an AI-powered answer!
        """
        self.speak("Here are the commands I can help with.")
        self.update_chat(help_text.strip(), "assistant")

    def speak(self, text: str):
        """Converts text to speech and updates the chat display."""
        self.update_chat(f"🤖 Assistant: {text}", "assistant")
        if self.engine:
            thread = threading.Thread(target=self._speak_worker, args=(text,))
            thread.daemon = True
            thread.start()

    def _speak_worker(self, text: str):
        """Worker function for text-to-speech engine."""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"TTS run-and-wait error: {e}")

    def update_chat(self, message: str, sender: str):
        """Updates the chat display with a new message."""
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp}] ")
        self.chat_display.insert(tk.END, f"{message}\n\n", sender)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)

    def update_status(self, status: str):
        """Updates the status bar text."""
        self.status_var.set(status)
        self.root.update_idletasks()

    def send_message(self, event=None):
        """Handles sending a message from the text entry field."""
        message = self.message_var.get().strip()
        if not message:
            return
        
        self.update_chat(f"👤 You: {message}", "user")
        self.message_var.set("")
        
        thread = threading.Thread(target=self.process_query, args=(message,))
        thread.daemon = True
        thread.start()

    def on_closing(self):
        """Handles the application window closing event."""
        if messagebox.askokcancel("Quit", "Do you want to quit the Desktop Assistant?"):
            self.cleanup()
            self.root.destroy()

    def cleanup(self):
        """Performs cleanup operations before exiting."""
        try:
            if self.engine:
                self.engine.stop()
            cv2.destroyAllWindows()
            self.logger.info("Application cleanup completed.")
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")

    def run(self):
        """Starts the main application loop."""
        try:
            self.update_chat("Desktop Assistant is ready! How can I help you today?", "system")
            self.speak("Desktop Assistant is ready. How can I help you?")
            self.root.mainloop()
        except Exception as e:
            self.logger.critical(f"A critical error occurred in the main loop: {e}")
            messagebox.showerror("Critical Error", f"An unrecoverable error occurred: {e}")
        finally:
            self.cleanup()

def main():
    """Main entry point for the application."""
    try:
        app = DesktopAssistant()
        app.run()
    except Exception as e:
        logging.basicConfig(level=logging.ERROR, filename='startup_error.log')
        logging.error(f"Failed to start the application: {e}", exc_info=True)
        print(f"Failed to start application. Check startup_error.log for details.")

if __name__ == "__main__":
    main()