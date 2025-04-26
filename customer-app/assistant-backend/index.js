import { exec } from "child_process";
import cors from "cors";
import dotenv from "dotenv";
import express from "express";
import { promises as fs } from "fs";
import { GoogleGenerativeAI } from "@google/generative-ai";
import { AgentForceClient } from "./agentforce.js";
import generateAudio from "./elevenlabs.js";
dotenv.config();

const gemini_api_key = process.env.GOOGLE_API_KEY;
const googleAI = new GoogleGenerativeAI(gemini_api_key);
const geminiConfig = {
  temperature: 0.9,
  topP: 1,
  topK: 1,
  maxOutputTokens: 4096,
};

const geminiModel = googleAI.getGenerativeModel({
  model: "gemini-2.0-flash",
  geminiConfig,
});

const elevenLabsApiKey = process.env.ELEVEN_LABS_API_KEY;
const voiceID = "EXAVITQu4vr4xnSDxMaL";
const agentForceClient = new AgentForceClient();

const app = express();
app.use(express.json());
app.use(cors());
const port = 3000;


app.get("/voices", async (req, res) => {
  res.send(await voice.getVoices(elevenLabsApiKey));
});

const execCommand = (command) => {
  return new Promise((resolve, reject) => {
    exec(command, (error, stdout, stderr) => {
      if (error) reject(error);
      resolve(stdout);
    });
  });
};

const lipSyncMessage = async (message) => {
  const time = new Date().getTime();
  console.log(`Starting conversion for message ${message}`);
  await execCommand(
    `sox audios/message_${message}.mp3 audios/message_${message}.wav`
  );
  console.log(`Conversion done in ${new Date().getTime() - time}ms`);
  await execCommand(
    `/Users/annu/Downloads/Rhubarb-Lip-Sync-1.14.0-macOS/rhubarb -f json -o audios/message_${message}.json audios/message_${message}.wav -r phonetic`
  );
};

const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const retryOperation = async (operation, maxRetries = MAX_RETRIES) => {
  let lastError;
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await operation();
    } catch (error) {
      console.error(`Attempt ${i + 1} failed:`, error.message);
      lastError = error;
      if (i < maxRetries - 1) {
        await sleep(RETRY_DELAY * (i + 1)); // Exponential backoff
      }
    }
  }
  throw lastError;
};

app.post("/chat", async (req, res) => {
  const userMessage = req.body.message;
  if (!userMessage) {
    res.send({
      messages: [
        {
          text: "Hey dear... How was your day?",
          audio: await audioFileToBase64("audios/intro_0.wav"),
          lipsync: await readJsonTranscript("audios/intro_0.json"),
          facialExpression: "smile",
          animation: "Talking_1",
        },
        {
          text: "I missed you so much... Please don't go for so long!",
          audio: await audioFileToBase64("audios/intro_1.wav"),
          lipsync: await readJsonTranscript("audios/intro_1.json"),
          facialExpression: "sad",
          animation: "Crying",
        },
      ],
    });
    return;
  }

  if (!elevenLabsApiKey || !gemini_api_key) {
    res.send({
      messages: [
        {
          text: "Please my dear, don't forget to add your API keys!",
          audio: await audioFileToBase64("audios/api_0.wav"),
          lipsync: await readJsonTranscript("audios/api_0.json"),
          facialExpression: "angry",
          animation: "Angry",
        },
        {
          text: "You don't want to ruin Wawa Sensei with a crazy Gemini and ElevenLabs bill, right?",
          audio: await audioFileToBase64("audios/api_1.wav"),
          lipsync: await readJsonTranscript("audios/api_1.json"),
          facialExpression: "smile",
          animation: "Laughing",
        },
      ],
    });
    return;
  }

  try {
    // Create or get existing session with AgentForce
    const agentId = process.env.SALESFORCE_AGENT_ID;
    const session = await retryOperation(() => agentForceClient.createSession(agentId));
    console.log("AgentForce session created:", session);

    // Send message to AgentForce with retry
    const agentResponse = await retryOperation(() => 
      agentForceClient.sendMessage(session.sessionId, userMessage)
    );
    console.log("AgentForce response:", agentResponse);

    // Extract the message from AgentForce response
    let agentMessage = "No response";
    if (agentResponse && agentResponse.messages && agentResponse.messages.length > 0) {
      agentMessage = agentResponse.messages[0].message || agentResponse.messages[0].text || "No response";
    }

    // Process AgentForce response through Gemini for facial expressions and animations
    const prompt = `
    You are a virtual assistant.
    You will always reply with a JSON array of messages. With a maximum of 3 messages.
    Each message has a text, facialExpression, and animation property.
    The different facial expressions are: smile, sad, angry, surprised, funnyFace, and default.
    The different animations are: Talking_0, Talking_1, Talking_2, Crying, Laughing, Rumba, Idle, Terrified, and Angry.
    
    AgentForce response: ${agentMessage}
    
    Respond with a valid JSON array of messages.
    `;

    const result = await retryOperation(() => geminiModel.generateContent(prompt));
    const response = result.response;
    const text = response.text();
    console.log("Raw response:", text);
    
    let messages;
    try {
      // Clean the text to ensure it's valid JSON
      const cleanedText = text.trim()
        .replace(/^```json\s*/, '')
        .replace(/^```\s*/, '')
        .replace(/\s*```$/, '');
      
      messages = JSON.parse(cleanedText);
      console.log("Parsed messages:", messages);
      
      // Ensure messages is an array
      if (!Array.isArray(messages)) {
        if (messages.messages) {
          messages = messages.messages;
        } else {
          messages = [messages];
        }
      }
    } catch (error) {
      console.error("Error parsing Gemini response:", error);
      console.error("Failed to parse text:", text);
      messages = [
        {
          text: "I'm sorry, I had trouble processing that. Could you try again?",
          facialExpression: "sad",
          animation: "Idle",
        },
      ];
    }

    // Process each message for audio and lip sync
    for (let i = 0; i < messages.length; i++) {
      const message = messages[i];
      console.log("Processing message:", message);
      
      try {
        // generate audio file
        const fileName = `audios/message_${i}.mp3`;
        const textInput = message.text;
        console.log("Generating audio for text:", textInput);
        
        // Ensure the ElevenLabs API key is properly formatted
        if (!elevenLabsApiKey || !elevenLabsApiKey.startsWith('sk_')) {
          throw new Error('Invalid ElevenLabs API key format');
        }

        await retryOperation(() => generateAudio(textInput, fileName));
        
        // generate lipsync
        await retryOperation(() => lipSyncMessage(i));
        message.audio = await audioFileToBase64(fileName);
        message.lipsync = await readJsonTranscript(`audios/message_${i}.json`);
      } catch (error) {
        console.error("Error processing message:", error);
        // Continue with the next message even if this one fails
        continue;
      }
    }

    res.send({ messages });
  } catch (error) {
    console.error("Error in chat endpoint:", error);
    res.status(500).send({
      error: "Failed to process request",
      details: error.message
    });
  }
});

const readJsonTranscript = async (file) => {
  const data = await fs.readFile(file, "utf8");
  return JSON.parse(data);
};

const audioFileToBase64 = async (file) => {
  const data = await fs.readFile(file);
  return data.toString("base64");
};

app.listen(port, () => {
  console.log(`Virtual Assistant listening on port ${port}`);
});
