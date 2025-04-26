import { useRef, useState, useEffect } from "react";
import { useChat } from "../hooks/useChat";
import { Mic, MicOff } from "lucide-react"; // Icon library
import { Button } from "./Button";

export const UI = ({ hidden, ...props }) => {
  const { chat, loading, message } = useChat();
  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const recognitionRef = useRef(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.error("Speech Recognition not supported in this browser");
      return;
    }

    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;

    recognition.continuous = true;
    recognition.lang = "en-US";

    recognition.onstart = () => setRecording(true);
    recognition.onresult = (event) => {
      const transcript = Array.from(event.results)
        .map((result) => result[0].transcript)
        .join("");
      setTranscript(transcript);
    };
    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      setRecording(false);
    };
    recognition.onend = () => setRecording(false);

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
      recognitionRef.current.stop();
      if (transcript.trim() && !loading && !message) {
        chat(transcript);
        setTranscript("");
      }
    } else {
      setTranscript("");
      recognitionRef.current.start();
    }
  };

  if (hidden) {
    return null;
  }

  return (
    <>
      <div className="fixed inset-0 z-10 flex justify-between p-6 flex-col pointer-events-none">
        <div className="flex items-center gap-6 pointer-events-auto max-w-2xl w-full mx-auto slide-up">

          {/* Text Display */}
          <div className="flex-1 min-h-[80px] p-6 rounded-2xl bg-white/70 backdrop-blur-lg shadow-lg border border-white/30 transition-all">
            <p className={`text-gray-900 text-lg font-medium tracking-wide leading-relaxed ${recording ? "animate-pulse" : ""}`}>
              {transcript || (recording ? "Listening..." : "Tap the mic to start speaking...")}
            </p>
          </div>

          {/* Microphone Button */}
          <Button
            disabled={loading || message}
            onClick={toggleRecording}
            variant={recording ? "danger" : "primary"}
            size="icon-lg"
            className={recording ? "animate-pulse shadow-2xl" : "shadow-2xl"}
          >
            {recording ? <MicOff size={32} className="text-white" /> : <Mic size={32} className="text-white" />}
          </Button>

        </div>
      </div>
    </>
  );
};
