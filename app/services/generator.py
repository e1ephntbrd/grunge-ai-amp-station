import io
from functools import lru_cache
from typing import Tuple

import numpy as np
from scipy.io import wavfile
import note_seq
from note_seq.protobuf import music_pb2
from note_seq.protobuf import generator_pb2
from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.models.shared import sequence_generator_bundle

from app.config import MODEL_PATH, SOUNDFONT_PATH, SAMPLE_RATE, CACHE_MAX_SIZE
from app.services.dsp import AudioDSP

NOTE_TO_PITCH = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3,
    "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
    "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
}

# Шлях до окремого важкого саундфонту для ритм-гітари
HEAVY_SF2_PATH = SOUNDFONT_PATH.parent / "bass.sf2"


class MusicGeneratorService:
    """
    Core backend service responsible for AI melody generation using Magenta (Basic RNN),
    dual SoundFont synthesis (Lead Solo + Heavy Power-Chord Rhythm), and RAM-based
    audio mixing.
    """

    generator = None

    @classmethod
    def initialize(cls):
        """Initializes and loads the Melody RNN sequence generator bundle and runs a warm-up."""
        if MODEL_PATH.exists():
            bundle = sequence_generator_bundle.read_bundle_file(str(MODEL_PATH))
            generator_map = melody_rnn_sequence_generator.get_generator_map()
            cls.generator = generator_map['basic_rnn'](checkpoint=None, bundle=bundle)
            cls.generator.initialize()
            print("🧠 Melody RNN успішно завантажено.")
        else:
            print(f"⚠️ Модель не знайдено: {MODEL_PATH}")

        cls._warmup()

    @classmethod
    def _warmup(cls):
        """Performs a test generation run to preload neural network weights into RAM."""
        try:
            cls.generate_audio_bytes(("E3", "G3", "A3"), 1.0, 18.0, 0.3, 3000.0)
            print("🔥 Warm-up успішно завершено.")
        except Exception as e:
            print(f"⚠️ Помилка Warm-up: {e}")

    @classmethod
    @lru_cache(maxsize=CACHE_MAX_SIZE)
    def generate_audio_bytes(
            cls,
            notes_tuple: Tuple[str, ...],
            temperature: float,
            distortion_gain: float,
            reverb: float,
            tone: float
    ) -> bytes:
        """
        Generates an AI grunge jam track combining a neural solo and a rhythm guitar track,
        processes them through an analog amp effect chain, and returns WAV audio bytes.

        Args:
            notes_tuple (Tuple[str, ...]): User-selected notes for the jam session.
            temperature (float): Creativity/randomness factor for the neural network.
            distortion_gain (float): Overdrive/distortion drive level in dB.
            reverb (float): Reverb wet mix level (0.0 to 1.0).
            tone (float): Low-pass filter cutoff frequency for tone control in Hz.

        Returns:
            bytes: Raw WAV audio file content stored in memory.
        """
        # 1. Створюємо послідовність для головного СОЛО
        solo_sequence = music_pb2.NoteSequence()
        solo_sequence.ticks_per_quarter = 220

        for i, note_name in enumerate(notes_tuple):
            letter = "".join([c for c in note_name if not c.isdigit()])
            octave = int("".join([c for c in note_name if c.isdigit()]))
            pitch = (octave + 1) * 12 + NOTE_TO_PITCH.get(letter, 0)

            solo_sequence.notes.add(
                pitch=pitch,
                start_time=i * 0.5,
                end_time=(i + 1) * 0.5,
                velocity=95,
                instrument=0
            )

        solo_sequence.total_time = len(notes_tuple) * 0.5

        # Налаштування довжини генерації AI (соло до 10 секунд)
        generator_options = generator_pb2.GeneratorOptions()
        generator_options.args['temperature'].float_value = temperature
        generator_options.generate_sections.add(
            start_time=solo_sequence.total_time,
            end_time=solo_sequence.total_time + 20.0
        )

        if cls.generator:
            generated_solo_sequence = cls.generator.generate(solo_sequence, generator_options)
        else:
            generated_solo_sequence = solo_sequence

        # 2. Створюємо окрему послідовність для РИТМ-ГІТАРИ (Живий рок-паттерн)
        rhythm_sequence = music_pb2.NoteSequence()
        rhythm_sequence.ticks_per_quarter = 220
        total_duration = generated_solo_sequence.total_time

        rock_pattern = [1, 0, 1, 1, 0, 1, 0, 1]
        step = 0.25
        current_time = 0.0
        note_index = 0
        pattern_idx = 0

        while current_time < total_duration:
            if rock_pattern[pattern_idx % len(rock_pattern)] == 1:
                base_note = notes_tuple[note_index % len(notes_tuple)]
                letter = "".join([c for c in base_note if not c.isdigit()])
                octave = 2  # Низький регістр для потужних павер-кордів
                root_pitch = (octave + 1) * 12 + NOTE_TO_PITCH.get(letter, 0)
                fifth_pitch = root_pitch + 7

                vel = 95 if pattern_idx % 4 == 0 else 75

                rhythm_sequence.notes.add(
                    pitch=root_pitch,
                    start_time=current_time,
                    end_time=current_time + 0.22,
                    velocity=vel,
                    instrument=1
                )
                rhythm_sequence.notes.add(
                    pitch=fifth_pitch,
                    start_time=current_time,
                    end_time=current_time + 0.22,
                    velocity=vel,
                    instrument=1
                )
                note_index += 1

            current_time += step
            pattern_idx += 1

        rhythm_sequence.total_time = total_duration

        # 3. Синтезуємо соло стандартним SoundFont
        audio_solo = note_seq.fluidsynth(
            generated_solo_sequence,
            sample_rate=SAMPLE_RATE,
            sf2_path=str(SOUNDFONT_PATH)
        )

        # Синтезуємо ритм спеціальним важким SoundFont (якщо він є, інакше бекап на основний)
        active_rhythm_sf2 = HEAVY_SF2_PATH if HEAVY_SF2_PATH.exists() else SOUNDFONT_PATH
        if not HEAVY_SF2_PATH.exists():
            print(f"⚠️ heavy_guitar.sf2 не знайдено, використовується стандартний SF2 для ритму.")

        audio_rhythm = note_seq.fluidsynth(
            rhythm_sequence,
            sample_rate=SAMPLE_RATE,
            sf2_path=str(active_rhythm_sf2)
        )

        # 4. Вирівнюємо масиви за довжиною та мікшуємо їх разом
        max_len = max(len(audio_solo), len(audio_rhythm))
        audio_solo = np.pad(audio_solo, (0, max_len - len(audio_solo)))
        audio_rhythm = np.pad(audio_rhythm, (0, max_len - len(audio_rhythm)))

        raw_audio = audio_solo + audio_rhythm

        # 5. Загальна обробка ефектів комбіка (Gain, Reverb, Tone)
        processed_audio = AudioDSP.apply_grunge_effects(
            raw_audio,
            SAMPLE_RATE,
            distortion_gain=distortion_gain,
            reverb=reverb,
            tone=tone
        )

        memory_file = io.BytesIO()
        wavfile.write(memory_file, SAMPLE_RATE, processed_audio)
        memory_file.seek(0)

        return memory_file.read()

