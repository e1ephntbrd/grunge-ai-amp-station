FROM python:3.8-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    fluidsynth \
    ffmpeg \
    libfluidsynth-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir --no-deps \
    magenta==2.1.4 \
    tensorflow-probability==0.17.0 \
    dm-tree \
    cloudpickle \
    tf-slim==1.1.0 \
    dm-sonnet==2.0.0 \
    scikit-image==0.19.3 \
    python-rtmidi==1.1.2 \
    pygtrie==2.5.0

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
