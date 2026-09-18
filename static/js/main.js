let selectedNotes = [];
let distortionEnabled = false;
let currentLoop = null;

// --- Tone.js Audio Bus ---
const soloVolume = new Tone.Volume(0).toDestination();
const rhythmVolume = new Tone.Volume(0).toDestination();

// Tone.Waveform: The oscilloscope is connected to the Master
const waveform = new Tone.Waveform(1024);
Tone.Destination.connect(waveform);

// Ch. I Generated solo
const chorus = new Tone.Chorus(4, 2.5, 0.5).connect(soloVolume).start();
const delay = new Tone.FeedbackDelay("8n", 0.3).connect(chorus);
const soloSynth = new Tone.Synth({
    oscillator: { type: "sawtooth" },
    envelope: { attack: 0.05, decay: 0.2, sustain: 0.5, release: 1 }
}).connect(delay);

// Ch. II Rhythm
const distortion = new Tone.Distortion(0.8);
const rhythmSynth = new Tone.PolySynth(Tone.Synth, {
    oscillator: { type: "fatsawtooth" },
    envelope: { attack: 0.1, decay: 0.3, sustain: 0.8, release: 1.2 }
});
rhythmSynth.connect(rhythmVolume);

// --- DOM Елементи ---
const keys = document.querySelectorAll('.key');
const pedal = document.getElementById('pedal-toggle');
const pedalLamp = document.getElementById('pedal-lamp');
const pedalStatus = document.getElementById('pedal-status');
const jamBtn = document.getElementById('btn-jam');
const stopBtn = document.getElementById('btn-stop');
const statusText = document.getElementById('status-text');

const sliderSolo = document.getElementById('vol-solo');
const sliderRhythm = document.getElementById('vol-rhythm');

// --- Canvas Visualizer ---
const canvas = document.getElementById('waveform');
const canvasCtx = canvas.getContext('2d');

function drawWaveform() {
    requestAnimationFrame(drawWaveform);

    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;

    const values = waveform.getValue();
    canvasCtx.fillStyle = '#000';
    canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

    canvasCtx.lineWidth = 2;
    canvasCtx.strokeStyle = distortionEnabled ? '#ff3333' : '#00ff66';
    canvasCtx.beginPath();

    const sliceWidth = canvas.width * 1.0 / values.length;
    let x = 0;

    for (let i = 0; i < values.length; i++) {
        const v = values[i];
        const y = (v + 1) / 2 * canvas.height;

        if (i === 0) {
            canvasCtx.moveTo(x, y);
        } else {
            canvasCtx.lineTo(x, y);
        }
        x += sliceWidth;
    }

    canvasCtx.lineTo(canvas.width, canvas.height / 2);
    canvasCtx.stroke();
}
drawWaveform();

// --- Stop & reset keyboards to initial state ---
function stopAudio() {
    console.log("Зупинка аудіо...");
    Tone.Transport.stop();
    Tone.Transport.cancel();

    if (currentLoop) {
        currentLoop.dispose();
        currentLoop = null;
    }

    try {
        soloSynth.triggerRelease();
        rhythmSynth.releaseAll();
    } catch (e) {
        console.warn("Помилка при скиданні нот:", e);
    }

    selectedNotes = [];
    keys.forEach(key => key.classList.remove('active'));

    statusText.textContent = "Звук зупинено. Оберіть ноти для нового джему.";
}

// Volume Controls
sliderSolo.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    soloVolume.volume.value = val <= -29 ? -Infinity : val;
});

sliderRhythm.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    rhythmVolume.volume.value = val <= -29 ? -Infinity : val;
});

// Keys selection
keys.forEach(key => {
    key.addEventListener('click', async () => {
        await Tone.start();
        const note = key.dataset.note;
        soloSynth.triggerAttackRelease(note, "8n");

        if (selectedNotes.includes(note)) {
            selectedNotes = selectedNotes.filter(n => n !== note);
            key.classList.remove('active');
        } else {
            if (selectedNotes.length < 3) {
                selectedNotes.push(note);
                key.classList.add('active');
            }
        }
        statusText.textContent = `Обрано ноти: ${selectedNotes.join(', ')}`;
    });
});

// Distortion Pedal
pedal.addEventListener('click', () => {
    distortionEnabled = !distortionEnabled;
    rhythmSynth.disconnect();

    if (distortionEnabled) {
        rhythmSynth.chain(distortion, rhythmVolume);
        pedalLamp.classList.add('active');
        pedalStatus.textContent = "[ ON ]";
        pedalStatus.style.color = "#ff5555";
    } else {
        rhythmSynth.connect(rhythmVolume);
        pedalLamp.classList.remove('active');
        pedalStatus.textContent = "[ OFF ]";
        pedalStatus.style.color = "#aaa";
    }
});

stopBtn.addEventListener('click', stopAudio);

// --- Jam API ---
jamBtn.addEventListener('click', async () => {
    console.log("Кнопка JAM натиснута. Обрані ноти:", selectedNotes);

    if (selectedNotes.length === 0) {
        alert("Будь ласка, оберіть хоча б одну ноту на клавіатурі!");
        return;
    }

    try {
        await Tone.start();
        console.log("Tone.js запущено.");

        // Зупиняємо попереднє відтворення перед відправкою запиту (АЛЕ НЕ очищаємо selectedNotes!)
        Tone.Transport.stop();
        Tone.Transport.cancel();
        if (currentLoop) {
            currentLoop.dispose();
            currentLoop = null;
        }

        statusText.textContent = "Генерація треку Magenta...";

        console.log("Надсилання fetch запиту до /generate...");
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notes: selectedNotes })
        });

        console.log("Статус відповіді сервера:", response.status);
        if (!response.ok) {
            throw new Error(`Помилка сервера: ${response.status}`);
        }

        const data = await response.json();
        console.log("Отримані дані від backend:", data);

        playSequence(data.solo, data.rhythm);
    } catch (err) {
        console.error("Помилка під час джему:", err);
        statusText.textContent = "Помилка джему: перевірте консоль браузера.";
    }
});

function playSequence(soloNotes, rhythmChords) {
    console.log("Запуск playSequence...", { soloNotes, rhythmChords });

    const stepDuration = 0.4;
    const chordDuration = 1.0;

    const totalSoloTime = soloNotes.length * stepDuration;
    const totalRhythmTime = rhythmChords.length * chordDuration;
    const loopDuration = Math.max(totalSoloTime, totalRhythmTime);

    currentLoop = new Tone.Loop((time) => {
        rhythmChords.forEach((chord, i) => {
            rhythmSynth.triggerAttackRelease(chord, "2n", time + (i * chordDuration));
        });

        soloNotes.forEach((note, i) => {
            soloSynth.triggerAttackRelease(note, "8n", time + (i * stepDuration));
        });
    }, loopDuration);

    currentLoop.start(0);
    Tone.Transport.start();

    statusText.textContent = "Грає зациклений гранж-джем! 🤘";
}
