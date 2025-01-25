#!/usr/bin/env python3
import subprocess
import sys
import os

def main():
    # --- 1️⃣ Install Dependencies Silently ---
    
    # 1c. cd Kokoro-82M
    # os.chdir("Kokoro-82M")
    
    # 1d. Install espeak-ng via apt-get (Linux-specific)
    
    # --- 2️⃣ Build the model and load the default voicepack ---
    import torch
    from models import build_model
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    MODEL = build_model('kokoro-v0_19.pth', device)
    
    VOICE_NAME = [
        'af', # Default voice is a 50-50 mix of Bella & Sarah
        'af_bella', 'af_sarah', 'am_adam', 'am_michael',
        'bf_emma', 'bf_isabella', 'bm_george', 'bm_lewis',
        'af_nicole', 'af_sky',
    ][0]
    
    VOICEPACK_PATH = f"voices/{VOICE_NAME}.pt"
    VOICEPACK = torch.load(VOICEPACK_PATH, weights_only=True).to(device)
    print(f"Loaded voice: {VOICE_NAME}")
    
    # --- 3️⃣ Generate the audio ---
    from kokoro import generate
    text = (
        "How could I know? It's an unanswerable question. "
        "Like asking an unborn child if they'll lead a good life. "
        "They haven't even been born."
    )
    
    # The 'lang' is determined by the first letter of VOICE_NAME:
    # a => en-us, b => en-gb, etc.
    audio, out_ps = generate(MODEL, text, VOICEPACK, lang=VOICE_NAME[0])
    
    # --- 4️⃣ Print the phonemes and optionally save audio ---
    print("Phonemes used:")
    print(out_ps)
    
    # Save audio to a WAV file (optional)
    # Requires 'soundfile' (pip install soundfile)
    try:
        import soundfile as sf
        sf.write("output.wav", audio, 24000)
        print("\nAudio written to 'output.wav' (24 kHz).")
    except ImportError:
        print("\nOptional: 'soundfile' is not installed, so no .wav file was created.")

if __name__ == "__main__":
    main()
