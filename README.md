# 🎸 Grunge AI Amp Station (MUD-AMP 90)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=flat-square&logo=fastapi&logoColor=white)
![TensorFlow](https://img.shields.io/badge/Magenta-AI-ff6f61?style=flat-square&logo=tensorflow&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)

A retro-styled web application that combines neural network melody generation (Magenta Melody RNN) with analog-emulated guitar DSP effects and a skeuomorphic vintage hardware interface. 

---

## ⚡ Key Features

* **Neural Solo & Heavy Rhythm:** Generates AI lead solos using Magenta's Melody RNN, paired with automated heavy power-chord rhythm tracks synthesized via dual SoundFonts (`FluidSynth`).
* **Vintage Analog DSP Chain:** Built-in audio processing using Spotify's `Pedalboard`, featuring:
  * High-pass filtering (cutting muddy low-end frequencies)
  * Overdrive / Distortion drive
  * Low-pass tone shaping
  * Room reverb and peak normalization for 16-bit PCM output.
* **Skeuomorphic Hardware UI:** Custom CSS-crafted interface mimicking a weathered guitar amplifier cabinet with a burlap/hessian texture, debossed/branded stamps, and functional analog knobs.
* **CRT Oscilloscope Visualizer:** Real-time waveform rendering powered by the Web Audio API Analyser node with scanlines and phosphor glow.

---

## 🛠️ Tech Stack

* **Backend:** Python, FastAPI, Magenta (TensorFlow), FluidSynth, Pedalboard, NumPy, SciPy
* **Frontend:** HTML5, CSS3 (Advanced gradients, custom textures, flexbox), Vanilla JavaScript (Web Audio API, Canvas)

---

## 🚀 Quick Start

### 1. Prerequisites & Dependencies
Ensure you have Python installed along with FluidSynth and required audio libraries.

{codeStart}bash
pip install -r requirements.txt
{codeEnd}

### 2. Run the Application

{codeStart}bash
python main.py
{codeEnd}

Open your browser and navigate to `http://localhost:8000` to fire up the amp.

---

## 📂 Project Structure

{codeStart}text
grunge-ai-amp-station/
│
├── static/
│   ├── app.js        # Client-side audio logic, knobs rotation, Web Audio API & oscilloscope
│   └── style.css     # Vintage cabinet styling, burlap texture, and debossed typography
├── templates/
│   └── index.html    # Main interface markup
├── main.py           # FastAPI server & route handlers
└── requirements.txt  # Python dependencies
{codeEnd}

---

## 📜 License
Distributed under the MIT License. See `LICENSE` for more information.
