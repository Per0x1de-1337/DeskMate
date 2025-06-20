# Use a slim Python base image
FROM python:3.9-slim-buster

# Set environment variables to prevent interactive prompts during build
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies required for GUI, Audio, and Camera
RUN apt-get update && apt-get install -y --no-install-recommends \
    # For Tkinter GUI
    python3-tk \
    # For PyAudio (microphone)
    portaudio19-dev \
    # For OpenCV (camera/GUI)
    libgl1-mesa-glx \
    libglib2.0-0 \
    # For pyttsx3 (text-to-speech)
    espeak \
    # Clean up apt cache to reduce image size
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install google-generativeai
# Copy the rest of the application code into the container
COPY Desktop_assistant.py .

# The command that will be run when the container starts
CMD ["python", "Desktop_assistant.py"]  