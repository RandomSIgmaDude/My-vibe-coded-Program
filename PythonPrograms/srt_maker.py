from faster_whisper import WhisperModel
from pathlib import Path

file_destination = r"" # a destination dir to save the .srt file **********************************************
groupbyword = charOrwordoreachgroup = None

# ============================================================
# List of available faster-whisper models (assigned to the model_size variable)
# The "parameters" figures are approximate; more parameters mean higher accuracy but slower speed and higher RAM/VRAM usage.
# ============================================================
#
# --- Multilingual Group (Supports Thai) ---
# "tiny"            # ~39M  Fastest, lightest, but least accurate. Often makes many mistakes with Thai.
# "base"            # ~74M  Lightweight, suitable for code testing.
# "small"           # ~244M The sweet spot suited for your machine (2GB VRAM).
# "medium"          # ~769M Noticeably more accurate, but heavy for 2GB VRAM (can try running on CPU instead).
# "large-v1"        # ~1550M First generation large model.
# "large-v2"        # ~1550M Improved version, widely used.
# "large-v3"        # ~1550M Newer version than v2, better language support.
# "large"           # Shortcut name, points to the latest large model defined by the library.
# "large-v3-turbo"  # ~809M Reduced decoder layers, much faster than large-v3 with similar accuracy.
# "turbo"           # Shortcut name for large-v3-turbo.
#
# --- English-only Group (.en) ---
# "tiny.en"         # For English audio only.
# "base.en"         # For English audio only.
# "small.en"        # For English audio only.
# "medium.en"       # For English audio only.
#
# --- Distil Group (Compressed models, faster, but focuses on English) ---
# "distil-small.en"     # Small and fast, English only.
# "distil-medium.en"    # English only.
# "distil-large-v2"     # English only.
# "distil-large-v3"     # English only.
# "distil-large-v3.5"   # English only (requires a newer version of faster-whisper).
#
# --- Custom Configuration ---
# "D:/path/to/model_folder"          # Model folder converted to CTranslate2 format.
# "Systran/faster-whisper-small"     # Repo name on Hugging Face
# ============================================================
model_size = "medium" #  model size(read the above) ************************************
device = "cpu" # what you want to process with
compute_type="int8" # idk what this is



def format_time(total_seconds: float) -> str:
    total_ms = round(total_seconds * 1000)
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, milliseconds = divmod(remainder, 1000)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def format_srt(segments, groupbyword, charOrwordoreachgroup) -> None:
    words = []
    print("Transcript:")
    for segment in segments:
        if segment.words:
            words.extend(segment.words)
            
    if not words:
        print("No words detected, nothing to write")
        return
        
    # ---------- Grouping Words ----------
    groups = []
    if groupbyword:
        # Word count mode: 4 words per group (equal steps and grabs, no duplicate words)
        for i in range(0, len(words), charOrwordoreachgroup):
            groups.append(words[i:i + charOrwordoreachgroup])
    else:
        # Character count mode: accumulate words until target is reached, then store the entire word that completes it
        group = []
        chars = 0
        for w in words:
            group.append(w)
            chars += sum(1 for ch in w.word if ch.isalnum())
            if chars >= charOrwordoreachgroup:
                groups.append(group)
                group = []
                chars = 0
        if group: # the last word
            groups.append(group)

    # ---------- write file ----------
    print("writing file")
    output_dir = Path(file_destination)
    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / "tranScript.srt"

    with open(file_path, "w", encoding="utf-8") as file:
        for count, group in enumerate(groups, start=1):
            start_time = group[0].start
            end_time = group[-1].end
            text = "".join(w.word for w in group).strip()

            file.write(f"{count}\n")
            file.write(f"{format_time(start_time)} --> {format_time(end_time)}\n")
            file.write(f"{text}\n\n")

    print(f"finished chcek out the .srt file in {file_destination}")


def transcribe_audio(audio_file, groupbyword, charOrwordoreachgroup):
    print(f"selecting model... (size: {model_size}, device: {device}, compute_type: {compute_type})")
    model = WhisperModel(
        model_size,
        device=device,
        compute_type=compute_type
    )

    print("Analyzing audio... please wait...")

    segments, info = model.transcribe(
        audio_file,
        language="en",
        beam_size=5,
        vad_filter=True,
        temperature=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
        word_timestamps=True
    )

    print(
        f"Detected language '{info.language}' "
        f"with {info.language_probability * 100:.1f}% confidence"
    )

    format_srt(segments, groupbyword, charOrwordoreachgroup)


if __name__ == "__main__":
    print("Welcome to the Speech Recognition Tool!")
    audio_file = input("Enter the path to the audio file path: ").strip().strip('"')
    if not Path(audio_file).is_file():
        raise SystemExit("File not found")

    groupbyword = input("Do you want to group the words by word? (y/n): ")
    groupbyword = True if groupbyword.lower() == "y" else False

    while True:
        try:
            charOrwordoreachgroup = int(input("Enter the number of characters or word per group (depends on the previous answer): "))
            if charOrwordoreachgroup >= 1:
                break
        except ValueError:
            pass
        print("Please enter a whole number that is 1 or more")

    print(f"""
group by word: {groupbyword},
char per group: {charOrwordoreachgroup}
""")
    
    input("Press Enter to start transcribing...")

    transcribe_audio(audio_file, groupbyword, charOrwordoreachgroup)