const chatBox = document.getElementById("chat-box");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");
const userInput = document.getElementById("user-input");
const chatBody = document.getElementById("chat-body");
const canvas = document.getElementById("waveform");
const ctx = canvas.getContext("2d");

const API_BASE = "http://127.0.0.1:5000";

// ✅ Fullscreen chatbot visible on load
window.addEventListener("DOMContentLoaded", () => {
  chatBox.style.display = "flex";
  chatBox.classList.add("fullscreen");

    appendMessage(
    "🤖 Hello! I’m your Disaster Safety Assistant.\nI can help you with disaster information, safehouse guidance, or detecting fake news. How can I assist you today?",
    "bot"
  );
});
// Append chat bubbles
function appendMessage(msg, type) {
  const div = document.createElement("div");
  div.className = type === "user" ? "user-msg" : "bot-msg";
  div.innerText = msg;
  chatBody.appendChild(div);
  chatBody.scrollTop = chatBody.scrollHeight;
}

// Send text message
async function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;
  appendMessage(text, "user");
  userInput.value = "";
  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      body: new URLSearchParams({ message: text }),
    });
    const data = await res.json();
    appendMessage(data.response || "⚠️ No response from server.", "bot");
  } catch {
    appendMessage("❌ Error connecting to backend.", "bot");
  }
}

sendBtn.onclick = sendMessage;
userInput.addEventListener("keypress", e => {
  if (e.key === "Enter") sendMessage();
});

// 🎙️ Voice + waveform
let mediaRecorder, audioChunks = [];
let audioContext, analyser, source, dataArray, animationId;

// Realistic waveform animation
function drawWaveform() {
  animationId = requestAnimationFrame(drawWaveform);
  const bufferLength = analyser.frequencyBinCount;
  dataArray = new Uint8Array(bufferLength);
  analyser.getByteFrequencyData(dataArray);
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  const numBars = 64;
  const step = Math.floor(bufferLength / numBars);
  const barWidth = canvas.width / numBars;

  for (let i = 0; i < numBars; i++) {
    const value = dataArray[i * step] / 255.0;
    const height = value * canvas.height * 0.9;
    const y = (canvas.height - height) / 2;

    // 🔥 Glowing red waveform bars
    const colorVal = Math.floor(150 + value * 105);
    ctx.fillStyle = `rgb(${colorVal}, ${40 + value * 60}, ${40 + value * 20})`;
    ctx.fillRect(i * barWidth + 1, y, barWidth - 2, height);
  }
}

// Mic recording handler
micBtn.onclick = async () => {
  if (!mediaRecorder || mediaRecorder.state === "inactive") {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder = new MediaRecorder(stream);
      audioChunks = [];

      audioContext = new AudioContext();
      source = audioContext.createMediaStreamSource(stream);
      analyser = audioContext.createAnalyser();
      analyser.fftSize = 512;
      source.connect(analyser);

      drawWaveform();
      micBtn.classList.add("recording");
      mediaRecorder.start();

      mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
      mediaRecorder.onstop = async () => {
        cancelAnimationFrame(animationId);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        const blob = new Blob(audioChunks, { type: "audio/webm" });
        const formData = new FormData();
        formData.append("file", blob, "audio.webm");
        try {
          const res = await fetch(`${API_BASE}/transcribe`, { method: "POST", body: formData });
          const data = await res.json();
          if (data.question) {
            appendMessage(`🎙️ (${data.language}) ${data.question}`, "user");
            appendMessage(data.response, "bot");
          } else appendMessage("⚠️ Could not recognize speech.", "bot");
        } catch {
          appendMessage("❌ Transcription failed.", "bot");
        }
      };

      // Auto-stop after 8 seconds
      setTimeout(() => {
        if (mediaRecorder.state !== "inactive") {
          mediaRecorder.stop();
          micBtn.classList.remove("recording");
        }
      }, 8000);
    } catch {
      appendMessage("🎤 Microphone access denied.", "bot");
    }
  }
};
