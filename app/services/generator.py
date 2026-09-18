import random
from typing import List, Dict
import note_seq
from note_seq.protobuf import music_pb2

# Набір гранжевих квінтакордів для ритм-секції
POWER_CHORDS = [
    ["E2", "B2", "E3"],  # E5
    ["G2", "D3", "G3"],  # G5
    ["A2", "E3", "A3"],  # A5
    ["C3", "G3", "C4"],  # C5
    ["D3", "A3", "D4"],  # D5
]

# Гранжева мінорна пентатоніка
PENTATONIC_SCALE = ["E3", "G3", "A3", "Bb3", "B3", "D4", "E4", "G4", "A4"]

def note_to_midi_pitch(note_str: str) -> int:
    """Універсальне конвертування ноти (наприклад "E3", "Bb3") у MIDI pitch."""
    try:
        return note_seq.note_name_to_midi(note_str)
    except AttributeError:
        # Резервна конвертація, якщо у версії note_seq назва функції відрізняється
        notes_map = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
                     'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
                     'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
        octave = int(note_str[-1])
        name = note_str[:-1]
        return (octave + 1) * 12 + notes_map[name]

class MusicGeneratorService:
    @classmethod
    def initialize(cls):
        """Ініціалізація сервісу."""
        pass

    @classmethod
    def generate_jam(cls, input_notes: List[str]) -> Dict[str, List]:
        return cls._generate_grunge_sequence(input_notes)

    @classmethod
    def _generate_grunge_sequence(cls, input_notes: List[str]) -> Dict[str, List]:
        sequence = music_pb2.NoteSequence()
        sequence.tempos.add(qpm=120.0)

        current_time = 0.0
        for note_str in input_notes:
            pitch = note_to_midi_pitch(note_str)
            sequence.notes.add(
                pitch=pitch,
                start_time=current_time,
                end_time=current_time + 0.5,
                velocity=80
            )
            current_time += 0.5

        # Генеруємо доліше соло (16 - 24 ноти замість 4-8)
        generated_solo = list(input_notes)
        extension_length = random.randint(16, 24)

        for _ in range(extension_length):
            next_note = random.choice(PENTATONIC_SCALE)
            generated_solo.append(next_note)

            pitch = note_to_midi_pitch(next_note)
            sequence.notes.add(
                pitch=pitch,
                start_time=current_time,
                end_time=current_time + 0.5,
                velocity=85
            )
            current_time += 0.5

        # Генеруємо 8 квінтакордів для ритм-секції (замість 4)
        generated_rhythm = [random.choice(POWER_CHORDS) for _ in range(8)]

        return {"solo": generated_solo, "rhythm": generated_rhythm}

# Ініціалізація
MusicGeneratorService.initialize()
