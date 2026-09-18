const selectedNotes = new Set();
const jamBtn = document.getElementById('jam-btn');
const stopBtn = document.getElementById('stop-btn');
const statusDiv = document.getElementById('status');
const audioPlayer = document.getElementById('audio-player');

const canvas = document.getElementById('oscilloscope');
const canvasCtx = canvas.getContext('2d');

// Єдиний глобальний аудіоконтекст для всього додатка
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

let analyser = null;
let sourceNode = null;

// Словник частот для нот (від C3 до B3)
const noteFrequencies = {
    "C3": 130.81,
    "D3": 146.83,
    "E3": 164.81,
    "F3": 174.61,
    "G3": 196.00,
    "A3": 220.00,
    "B3": 246.94
};

// Зв'язок слайдерів з візуальними крутилками та обертання
function setupKnobs() {
    const knobsData = [
        { slider: 'gain-slider', knob: 'knob-gain', min: 1, max: 30 },
        { slider: 'reverb-slider', knob: 'knob-reverb', min: 0, max: 1 },
        { slider: 'tone-slider', knob: 'knob-tone', min: 500, max: 8000 }
    ];

    knobsData.forEach(item => {
        const slider = document.getElementById(item.slider);
        const knob = document.getElementById(item.knob);

        if (!slider || !knob) return;

        const updateKnobRotation = () => {
            const val = parseFloat(slider.value);
            const min = parseFloat(slider.min);
            const max = parseFloat(slider.max);
            // Перетворюємо значення в кут від -135 до 135 градусів
            const percentage = (val - min) / (max - min);
            const deg = percentage * 270 - 135;
            knob.style.transform = `rotate(${deg}deg)`;
        };

        slider.addEventListener('input', updateKnobRotation);
        updateKnobRotation(); // Ініціалізація початкового положення
    });
}

setupKnobs();

function playTone(noteName) {
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }

    const freq = noteFrequencies[noteName];
    if (!freq) return;

    const oscillator = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();

    oscillator.type = 'sawtooth';
    oscillator.frequency.setValueAtTime(freq, audioCtx.currentTime);

    const filter = audioCtx.createBiquadFilter();
    filter.type = 'lowpass';
    filter.frequency.setValueAtTime(3000, audioCtx.currentTime);

    gainNode.gain.setValueAtTime(0.3, audioCtx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.5);

    oscillator.connect(filter);
    filter.connect(gainNode);
    gainNode.connect(audioCtx.destination);

    oscillator.start();
    oscillator.stop(audioCtx.currentTime + 0.5);
}

// Вибір нот
document.querySelectorAll('.key').forEach(key => {
    key.addEventListener('click', () => {
        if (key.disabled) return;
        const note = key.getAttribute('data-note');

        playTone(note);

        if (selectedNotes.has(note)) {
            selectedNotes.delete(note);
            key.classList.remove('active');
        } else {
            selectedNotes.add(note);
            key.classList.add('active');
        }
    });
});

// Функція блокування/розблокування елементів інтерфейсу
function setInterfaceLocked(locked) {
    jamBtn.disabled = locked;

    // Блокуємо/розблокуємо клавіші піаніно
    document.querySelectorAll('.key').forEach(key => {
        key.disabled = locked;
    });

    // Блокуємо/розблокуємо слайдери крутилок
    document.querySelectorAll('.knob-control input[type="range"]').forEach(slider => {
        slider.disabled = locked;
    });
}

// Загальна функція для скидання вибору нот та розблокування інтерфейсу
function resetSelectionAndInterface() {
    selectedNotes.clear();
    document.querySelectorAll('.key').forEach(key => {
        key.classList.remove('active');
    });
    setInterfaceLocked(false);
}

// Налаштування Web Audio Analyser для осцилографа
function setupVisualizer(audioElement) {
    if (!analyser) {
        analyser = audioCtx.createAnalyser();
        analyser.fftSize = 2048;

        sourceNode = audioCtx.createMediaElementSource(audioElement);
        sourceNode.connect(analyser);
        analyser.connect(audioCtx.destination);
    }
    if (audioCtx.state === 'suspended') {
        audioCtx.resume();
    }
    drawOscillator();
}

function drawOscillator() {
    requestAnimationFrame(drawOscillator);
    if (!analyser) return;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    analyser.getByteTimeDomainData(dataArray);

    canvasCtx.fillStyle = 'rgba(18, 14, 12, 0.4)';
    canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

    canvasCtx.lineWidth = 2;
    canvasCtx.strokeStyle = '#ff4500'; // Ламповий помаранчево-червоний колір
    canvasCtx.beginPath();

    const sliceWidth = canvas.width / bufferLength;
    let x = 0;

    for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0;
        const y = v * (canvas.height / 2);

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

// Обробник натискання на кнопку STOP / RESET
stopBtn.addEventListener('click', () => {
    if (audioPlayer) {
        audioPlayer.pause();
        audioPlayer.currentTime = 0;
        audioPlayer.src = "";
    }

    resetSelectionAndInterface();

    statusDiv.textContent = 'ГОТОВИЙ ДО РОБОТИ';
    console.log("🛑 Відтворення зупинено, вибір скинуто.");
});

// Автоматичне скидання і розблокування, коли трек закінчився сам
audioPlayer.addEventListener('ended', () => {
    resetSelectionAndInterface();
    statusDiv.textContent = 'ТРЕК ЗАВЕРШЕНО';
});

// Запуск джему
jamBtn.addEventListener('click', async () => {
    if (selectedNotes.size === 0) {
        alert('Оберіть хоча б одну ноту!');
        return;
    }

    const gainValue = parseFloat(document.getElementById('gain-slider')?.value || 18.0);
    const reverbValue = parseFloat(document.getElementById('reverb-slider')?.value || 0.3);
    const toneValue = parseFloat(document.getElementById('tone-slider')?.value || 3000);

    statusDiv.textContent = '⚡ ГЕНЕРАЦІЯ AI-СОЛО ТА СИНТЕЗ В RAM...';

    // Блокуємо весь інтерфейс на час генерації та гри
    setInterfaceLocked(true);

    try {
        const response = await fetch('/api/generate-audio-stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                notes: Array.from(selectedNotes),
                temperature: 1.0,
                distortion_gain: gainValue,
                reverb: reverbValue,
                tone: toneValue
            })
        });

        if (!response.ok) throw new Error('Помилка генерації');

        const blob = await response.blob();
        const audioUrl = URL.createObjectURL(blob);

        audioPlayer.src = audioUrl;
        setupVisualizer(audioPlayer);
        audioPlayer.play();

        statusDiv.textContent = '🎸 ГРАЄ AI GRUNGE КАБІНЕТ!';
    } catch (err) {
        statusDiv.textContent = '❌ ПОМИЛКА ГЕНЕРАЦІЇ АУДІО';
        console.error(err);
        setInterfaceLocked(false); // Розблоковуємо у разі помилки
    }
});
