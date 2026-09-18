import numpy as np
from pedalboard import Pedalboard, Distortion, Reverb, HighpassFilter, LowpassFilter


class AudioDSP:
    """
    Digital Signal Processing (DSP) utility for shaping and enhancing
    raw audio streams with authentic vintage guitar amplifier characteristics.
    """

    @staticmethod
    def apply_grunge_effects(
            audio_data: np.ndarray,
            sample_rate: int,
            distortion_gain: float = 15.0,
            reverb: float = 0.3,
            tone: float = 3000.0
    ) -> np.ndarray:
        """
        Applies a simulated grunge guitar amplifier effect chain to the input audio

        Args:
            audio_data (np.ndarray): Raw input audio array (typically normalized within [-1.0, 1.0])
            sample_rate (int): Sampling rate of the audio in Hertz (e.g., 44100)
            distortion_gain (float, optional): Distortion drive level in decibels (dB). Defaults to 15.0
            reverb (float, optional): Reverb wet signal level, ranging from 0.0 to 1.0. Defaults to 0.3
            tone (float, optional): Low-pass filter cutoff frequency in Hz for tone control. Defaults to 3000.0

        Returns:
            np.ndarray: Processed audio array normalized and converted to 16-bit PCM format (int16) suitable for WAV export
        """
        if len(audio_data) == 0:
            return audio_data

        # note_seq.fluidsynth діапазон [-1.0, 1.0]
        float_audio = audio_data.astype(np.float32)

        # Збираємо ланцюжок ефектів гітарного комбіка
        board = Pedalboard([
            # Зрізаємо непотрібний бубнявий низ
            HighpassFilter(cutoff_frequency_hz=80.0),

            # Перевантаження (GAIN)
            Distortion(drive_db=distortion_gain),

            # Регулювання тембру (TONE)
            LowpassFilter(cutoff_frequency_hz=tone),

            # Об'єм та простір (REVERB)
            Reverb(room_size=0.5, damping=0.5, wet_level=reverb, dry_level=0.8)
        ])

        # Застосовуємо ефекти
        processed = board(float_audio, sample_rate)

        # Запобігаємо кліпінгу та нормалізуємо піки
        max_val = np.max(np.abs(processed))
        if max_val > 0:
            processed = processed / max_val * 0.85

        # Повертаємо назад у формат int16 для WAV
        return (processed * 32767.0).astype(np.int16)

