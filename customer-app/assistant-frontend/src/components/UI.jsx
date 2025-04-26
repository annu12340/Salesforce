import { useRef, useState, useEffect } from "react";
import { useChat } from "../hooks/useChat";

export const UI = ({ hidden, ...props }) => {
  const { chat, loading, message } = useChat();
  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Initialize speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.error("Speech Recognition not supported in this browser");
      return;
    }
    
    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;
    
    // Set properties
    recognition.continuous = true;
    recognition.lang = "en-US";
    
    // Event listeners
    recognition.onstart = () => {
      console.log("Speech recognition started");
      setRecording(true);
    };
    
    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map(result => result[0].transcript)
        .join("");
      
      setTranscript(transcript);
    };
    
    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      setRecording(false);
    };
    
    recognition.onend = () => {
      console.log("Speech recognition ended");
      setRecording(false);
    };
    
    // Cleanup function
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const toggleRecording = () => {
    if (!recognitionRef.current) {
      console.error("Speech Recognition not initialized");
      return;
    }
    
    if (recording) {
      // Stop recording and send the message
      recognitionRef.current.stop();
      if (transcript.trim() && !loading && !message) {
        chat(transcript);
        setTranscript("");
      }
    } else {
      // Start recording
      setTranscript("");
      recognitionRef.current.start();
    }
  };

  if (hidden) {
    return null;
  }

  return (
    <>
      <div className="fixed top-0 left-0 right-0 bottom-0 z-10 flex justify-between p-4 flex-col pointer-events-none">
        <div className="flex items-center gap-2 pointer-events-auto max-w-screen-sm w-full mx-auto">
          <div className="w-full p-4 rounded-md bg-opacity-50 bg-white backdrop-blur-md flex items-center">
            <span className="text-gray-800 italic">
              {transcript || (recording ? "Listening..." : "Click to speak...")}
            </span>
          </div>
          <button
            disabled={loading || message}
            onClick={toggleRecording}
            className={`${
              recording ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600'
            } text-white p-4 px-10 font-semibold uppercase rounded-md ${
              loading || message ? "cursor-not-allowed opacity-30" : ""
            }`}
          >
            {recording ? "Stop" : "Speak"}
          </button>
        </div>
      </div>
    </>
  );
};
