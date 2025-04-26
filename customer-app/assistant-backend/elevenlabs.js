import axios from 'axios';
import fs from 'fs';
import dotenv from 'dotenv';
dotenv.config();

const apiKey = process.env.ELEVEN_LABS_API_KEY;
const voiceId = '21m00Tcm4TlvDq8ikWAM'; // Rachel voice ID from ElevenLabs

async function generateAudio(text, outputPath) {
  try {
    if (!apiKey || !apiKey.startsWith('sk_')) {
      throw new Error('Invalid ElevenLabs API key format');
    }

    const response = await axios({
      method: 'post',
      url: `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
      headers: {
        'Accept': 'audio/mpeg',
        'Content-Type': 'application/json',
        'xi-api-key': apiKey,
      },
      data: {
        text: text,
        model_id: "eleven_monolingual_v1",
        voice_settings: {
          stability: 0.5,
          similarity_boost: 0.75,
          style: 0.5,
          use_speaker_boost: true
        }
      },
      responseType: 'arraybuffer'
    });

    // Ensure the directory exists
    const directory = outputPath.substring(0, outputPath.lastIndexOf('/'));
    if (!fs.existsSync(directory)) {
      fs.mkdirSync(directory, { recursive: true });
    }

    // Save the file
    fs.writeFileSync(outputPath, response.data);
    console.log(`Audio file saved as ${outputPath}`);
    return true;
  } catch (error) {
    console.error('Error generating audio:', error.response ? error.response.data : error.message);
    throw error;
  }
}

export default generateAudio; 