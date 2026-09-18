from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "basic_rnn.mag"
SOUNDFONT_PATH = BASE_DIR / "soundfonts" / "electric_guit.sf2"

SAMPLE_RATE = 22050
CHUNK_SIZE = 4096
CACHE_MAX_SIZE = 256
