from tkinter import *
import pyttsx3 
import speech_recognition as sr 
import datetime
import wikipedia 	
import webbrowser
import os
import openai
import cv2

openai.api_key = "REDACTED"
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

root = Tk()
root.title('Desktop Assistant')
root.geometry('750x475')

chatWindow = Text(root, bd=1, bg='green', width=60, height=20)
chatWindow.place(x=6, y=6, height=320, width=738)

messageWindow = Text(root, bd=1, bg='darkgrey', width=50, height=8)
messageWindow.place(x=6, y=340, height=115, width=590)

def speak(audio):
    chatWindow.insert(END, "Assistant: " + audio + "\n\n")
    engine.say(audio)
    engine.runAndWait()
    

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")    
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
        messageWindow.insert(END, query)
        return query
    except Exception as e:
        print("Say that again please...")  
        return "None"
    
def process_query(query):
    if 'wikipedia' in query:
        speak('Searching Wikipedia...')
        query = query.replace("wikipedia", "")
        results = wikipedia.summary(query, sentences=2)
        speak("According to Wikipedia")
        speak(results)
    elif 'open youtube' in query:
        webbrowser.open("youtube.com")
    elif 'open google' in query:
        webbrowser.open("google.com")    

    elif 'time' in query:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")    
        speak(f"Sir, the time is {strTime}")
    elif 'make folder' in query:
        folder_name = query.split("make folder", 1)[1].strip()
        try:
            os.mkdir(folder_name)
            chatWindow.insert(END, "Assistant: Folder '" + folder_name + "' created\n\n")  # Display folder creation response
            speak("Folder '" + folder_name + "' created")
        except Exception as e:
            chatWindow.insert(END, "Assistant: Failed to create folder\n\n")  # Display folder creation failure response
            speak("Failed to create folder")
    elif 'record video' in query:
        # Record a video
        cap = cv2.VideoCapture(0)
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('captured_video.avi', fourcc, 20.0, (640, 480))

        recording_time = 10  # Recording for 10 seconds
        start_time = datetime.datetime.now()

        while (datetime.datetime.now() - start_time).total_seconds() < recording_time:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
                cv2.imshow('Video Recording...', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                chatWindow.insert(END, "Assistant: Failed to record video\n\n")  # Display failure response
                speak("Failed to record video")
                break        

    elif 'capture photo' in query:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite("captured_photo.jpg", frame)
            chatWindow.insert(END, "Assistant: Photo captured\n\n")  # Display photo capture response
            speak("Photo captured")
        else:
            chatWindow.insert(END, "Assistant: Failed to capture photo\n\n")  # Display failure response
            speak("Failed to capture photo")

        cap.release()        
    elif 'create file' in query:
        file_content = query.split("create file", 1)[1].strip()
        try:
            with open("user_file.txt", "w") as file:
                file.write(file_content)
            chatWindow.insert(END, "Assistant: File 'user_file.txt' created with specified content\n\n")  # Display file creation response
            speak("File 'user_file.txt' created with specified content")
        except Exception as e:
            chatWindow.insert(END, "Assistant: Failed to create file\n\n")  # Display failure response
            speak("Failed to create file")    
    elif 'search on YouTube' in query:
        search_query = query.split("search on YouTube", 1)[1].strip()
        youtube_search_url = f"https://www.youtube.com/results?search_query={search_query}"
        try:
            webbrowser.open(youtube_search_url)  # Open the default web browser with the YouTube search URL
            chatWindow.insert(END, f"Assistant: Searching YouTube for '{search_query}'\n\n")  # Display search response
        except Exception as e:
            chatWindow.insert(END, "Assistant: Failed to perform YouTube search\n\n")  # Display failure response
            speak("Failed to perform YouTube search")
    elif 'search on youTube' in query:
        search_query = query.split("search on YouTube", 1)[1].strip()
        youtube_search_url = f"https://www.youtube.com/results?search_query={search_query}"
        try:
            webbrowser.open(youtube_search_url)  # Open the default web browser with the YouTube search URL
            chatWindow.insert(END, f"Assistant: Searching YouTube for '{search_query}'\n\n")  # Display search response
        except Exception as e:
            chatWindow.insert(END, "Assistant: Failed to perform YouTube search\n\n")  # Display failure response
            speak("Failed to perform YouTube search")
    elif 'search on google' in query:
        search_query = query.split("search on google", 1)[1].strip()
        google_search_url = f"https://www.google.com/search?q={search_query}"
        try:
            webbrowser.open(google_search_url)  # Open the default web browser with the YouTube search URL
            chatWindow.insert(END, f"Assistant: Searching Google for '{search_query}'\n\n")  # Display search response
        except Exception as e:
            chatWindow.insert(END, "Assistant: Failed to perform Google search\n\n")  # Display failure response
            speak("Failed to perform google search")        
                             
    else:
        completion = openai.ChatCompletion.create(model="gpt-4", messages=[{"role": "user", "content": query}])
        response = completion.choices[0].message.content
        speak(response)
    
    

def send_message():
    message = messageWindow.get("1.0", END)
    messageWindow.delete("1.0", END)
    chatWindow.insert(END, "User: " + message + "\n\n")
    process_query(message)

btn = Button(root, text='SEND', bg='grey', bd=5, activebackground='lightgrey', command=send_message, padx=20, pady=16, font=('Arial', 12))
btn.place(x=620, y=340)

def activate_microphone():
    query = takeCommand().lower()
    process_query(query)

btn_2 = Button(root, text='MIC', bg='grey', bd=5, activebackground='lightgrey', command=activate_microphone, padx=28, pady=8, font=('Arial', 12))
btn_2.place(x=620, y=400)
root.bind('<Alt-Return>', send_message)

root.mainloop()


