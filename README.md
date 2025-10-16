# Qwen3-ASR-Toolkit

[![PyPI version](https://badge.fury.io/py/qwen3-asr-toolkit.svg)](https://badge.fury.io/py/qwen3-asr-toolkit)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An advanced, high-performance Python command-line toolkit for using the **Qwen-ASR API** (formerly Qwen3-ASR-Flash). This implementation overcomes the API's 3-minute audio length limitation by intelligently splitting long audio/video files and processing them in parallel, enabling rapid transcription of hours-long content.

## 🚀 Key Features

-   **Break the 3-Minute Limit**: Seamlessly transcribe audio and video files of any length by bypassing the official API's duration constraint.
-   **Smart Audio Splitting**: Utilizes **Voice Activity Detection (VAD)** to split audio into meaningful chunks at natural silent pauses. This ensures that words and sentences are not awkwardly cut off.
-   **High-Speed Parallel Processing**: Leverages multi-threading to send audio chunks to the Qwen-ASR API concurrently, dramatically reducing the total transcription time for long files.
-   **Intelligent Post-Processing**: Automatically detects and removes common ASR **hallucinations and repetitive artifacts** for cleaner, more accurate transcripts.
-   **SRT Subtitle Generation**: Automatically create timestamped **`.srt` subtitle files** based on VAD segments, perfect for adding captions to video content.
-   **Automatic Audio Resampling**: Automatically converts audio from any sample rate and channel count to the 16kHz mono format required by the Qwen-ASR API. You can use any audio file without worrying about pre-processing.
-   **Universal Media Support**: Supports virtually any audio and video format (e.g., `.mp4`, `.mov`, `.mkv`, `.mp3`, `.wav`, `.m4a`) thanks to its reliance on FFmpeg.
-   **Simple & Easy to Use**: A straightforward command-line interface allows you to get started with just a single command.

## ⚙️ How It Works

This tool follows a robust pipeline to deliver fast and accurate transcriptions for long-form media:

1.  **Media Loading**: The script first loads your media file, whether it's a **local file or a remote URL**.
2.  **VAD-based Chunking**: It analyzes the audio stream using Voice Activity Detection (VAD) to identify silent segments.
3.  **Intelligent Splitting**: The audio is then split into smaller chunks based on the detected silences. Each chunk's duration is managed to stay under the 3-minute API limit, with a **user-configurable target length (defaulting to 120 seconds)**, preventing mid-sentence cuts.
4.  **Parallel API Calls**: A thread pool is initiated to upload and process these chunks concurrently using the DashScope Qwen-ASR API.
5.  **Result Aggregation & Cleaning**: The transcribed text segments from all chunks are collected, re-ordered, and then **post-processed to remove detected repetitions and hallucinations**.
6.  **Output Generation**: The final, cleaned transcription is printed to the console and saved to a `.txt` file. **Optionally, a timestamped `.srt` subtitle file can also be generated.**

### 🔍 Voice Activity Detection in Detail

The toolkit performs VAD locally so that long recordings can be segmented before they are sent to the DashScope API. The implementation in `qwen3_asr_toolkit/audio_tools.py` and `qwen3_asr_toolkit/call_api.py` follows these steps:

#### What is the Silero VAD model?

The project depends on the lightweight **Silero Voice Activity Detector**, a small TorchScript model released by the Silero/Snakers4 team for offline speech boundary detection. It is bundled through the [`silero-vad` Python package](https://pypi.org/project/silero-vad/) and is loaded locally via `silero_vad.get_speech_timestamps`, which returns sample-level start and end indices for every region that likely contains human speech.【F:qwen3_asr_toolkit/audio_tools.py†L1-L73】 Because the model runs entirely on the client, no extra API calls are required—only the already-downloaded parameters are used during segmentation.【F:qwen3_asr_toolkit/call_api.py†L62-L110】

1.  **Model Preparation**: When the CLI receives an input longer than three minutes, it loads the Silero VAD model in the worker process and keeps it in memory for reuse across segments.【F:qwen3_asr_toolkit/call_api.py†L62-L86】
2.  **Speech Timestamp Detection**: `process_vad` runs `get_speech_timestamps` on the mono, 16 kHz waveform to identify the start and end sample of each speech region. Detection parameters enforce a minimum speech duration of 1.5 seconds and a minimum silence duration of 0.5 seconds to avoid choppy splits.【F:qwen3_asr_toolkit/audio_tools.py†L47-L71】
3.  **Target-Length Splitting**: The function seeds candidate split points with detected boundaries, then walks forward in steps of the user-defined `segment_threshold_s` (default 120 seconds), snapping each desired boundary to the closest speech-aligned point. This keeps chunks near the target duration while respecting speech pauses.【F:qwen3_asr_toolkit/audio_tools.py†L71-L89】
4.  **Maximum-Length Enforcement**: After the initial pass, any chunk longer than `max_segment_threshold_s` (default 180 seconds) is subdivided evenly to ensure that no segment exceeds the API’s limit even when long speech spans lack silence.【F:qwen3_asr_toolkit/audio_tools.py†L91-L110】
5.  **Chunk Assembly**: The resulting split points are converted into `(start_sample, end_sample, wav_slice)` tuples, which the CLI serializes to temporary files before uploading them in parallel. Timestamps are later reused for subtitle generation.【F:qwen3_asr_toolkit/audio_tools.py†L111-L116】【F:qwen3_asr_toolkit/call_api.py†L86-L140】
6.  **Robust Fallback**: If Silero VAD fails (e.g., due to model errors or truly silent audio), the code falls back to deterministic chunking that simply slices the waveform into consecutive `max_segment_threshold_s` windows, guaranteeing progress without remote retries.【F:qwen3_asr_toolkit/audio_tools.py†L118-L136】

Because all of these steps execute locally, no raw audio beyond the short VAD-derived segments is sent to the API until after chunking is complete.

## 🏁 Getting Started

Follow these steps to set up and run the project on your local machine.

### Prerequisites

-   Python 3.8 or higher.
-   **FFmpeg**: The script requires FFmpeg to be installed on your system to handle media files.
    -   **Ubuntu/Debian**: `sudo apt update && sudo apt install ffmpeg`
    -   **macOS**: `brew install ffmpeg`
    -   **Windows**: Download from the [official FFmpeg website](https://ffmpeg.org/download.html) and add it to your system's PATH.
-   **DashScope API Key**: You need an API key from Alibaba Cloud's DashScope.
    -   You can obtain one from the [DashScope Console](https://dashscope.console.aliyun.com/apiKey). If you are calling the API services of Tongyi Qwen for the first time, you can follow the tutorial on [this website](https://help.aliyun.com/zh/model-studio/first-api-call-to-qwen) to create your own API Key.
    -   For better security and convenience, it is **highly recommended** to set your API key as an environment variable named `DASHSCOPE_API_KEY`. The script will automatically use it, and you won't need to pass the `--api-key` argument in the command.

        **On Linux/macOS:**
        ```bash
        export DASHSCOPE_API_KEY="your_api_key_here"
        ```
        *(To make this permanent, add the line to your `~/.bashrc`, `~/.zshrc`, or `~/.profile` file.)*

        **On Windows (Command Prompt):**
        ```cmd
        set DASHSCOPE_API_KEY="your_api_key_here"
        ```

        **On Windows (PowerShell):**
        ```powershell
        $env:DASHSCOPE_API_KEY="your_api_key_here"
        ```
        *(For a permanent setting on Windows, search for "Edit the system environment variables" in the Start Menu and add `DASHSCOPE_API_KEY` to your user variables.)*

### Installation

We recommend installing the tool directly from PyPI for the simplest setup.

#### Option 1: Install from PyPI (Recommended)

Simply run the following command in your terminal. This will install the package and make the `qwen3-asr` command available system-wide.

```bash
pip install qwen3-asr-toolkit
```

#### Option 2: Install from Source

If you want to install the latest development version or contribute to the project, you can install from the source code.

1.  Clone the repository:
    ```bash
    git clone https://github.com/QwenLM/Qwen3-ASR-Toolkit.git
    cd Qwen3-ASR-Toolkit
    ```

2.  Install the package:
    ```bash
    pip install .
    ```

## 📖 Usage

Once installed, you can use the `qwen3-asr` command directly from your terminal. By default, the tool will print progress information.

### Command

```bash
qwen3-asr -i <input_file_or_url> [-key <api_key>] [-j <num_threads>] [-c <context>] [-d <duration>] [-t <tmp_dir>] [--save-srt] [-s]
```

### Arguments

| Argument                  | Short  | Description                                                                          | Required/Optional                        |
| ------------------------- | ------ | ------------------------------------------------------------------------------------ | ---------------------------------------- |
| `--input-file`            | `-i`   | Path to the local media file or a remote URL (http/https) to transcribe.             | **Required**                             |
| `--context`               | `-c`   | Text context to guide the ASR model, improving recognition of specific terms.        | Optional, Default: `""`                  |
| `--dashscope-api-key`     | `-key` | Your DashScope API Key.                                                              | Optional (if `DASHSCOPE_API_KEY` is set) |
| `--num-threads`           | `-j`   | The number of concurrent threads to use for API calls.                               | Optional, **Default: 4**                 |
| `--vad-segment-threshold` | `-d`   | Target duration in seconds for each VAD-split audio chunk.                           | Optional, **Default: 120**               |
| `--tmp-dir`               | `-t`   | Path to a directory for storing temporary chunk files.                               | Optional, Default: `~/qwen3-asr-cache`   |
| `--save-srt`              | `-srt` | Generate and save a timestamped SRT subtitle file in addition to the `.txt` file.    | Optional                                 |
| `--silence`               | `-s`   | Silence mode. Suppresses detailed progress and chunking information on the terminal. | Optional                                 |

### Output

The full transcription result will be printed to the terminal (unless in `--silence` mode) and also saved in a `.txt` file in the same directory as the input file. For example, if you process `my_video.mp4`, the output will be saved to `my_video.txt`.

**If you use the `--save-srt` flag, a corresponding `my_video.srt` subtitle file will also be created in the same directory.**

---

## ✨ Examples

Here are a few examples of how to use the tool.

#### 1. Basic Transcription of a Local File

Transcribe a video file using the default 4 threads. This command assumes you have set the `DASHSCOPE_API_KEY` environment variable.

```bash
qwen3-asr -i "/path/to/my/long_lecture.mp4"
```

#### 2. Transcribe a Remote Audio File

Directly process an audio file from a URL.

```bash
qwen3-asr -i "https://somewebsite.com/audios/podcast_episode.mp3"
```

#### 3. Generate an SRT Subtitle File

Use the `--save-srt` (or `-srt`) flag to generate a timestamped subtitle file alongside the plain text transcript. This is ideal for video captioning.

```bash
qwen3-asr -i "/path/to/my/documentary.mp4" -srt
```
*This command will create `documentary.txt` and `documentary.srt`.*

#### 4. Increase Concurrency and Pass API Key

Transcribe a long audio file using 8 parallel threads and pass the API key directly via the command line.

```bash
qwen3-asr -i "/path/to/my/podcast_episode_01.wav" -j 8 -key "your_api_key_here"
```

#### 5. Provide Context and Customize Chunk Duration

If your audio contains specific jargon, use the `-c` flag. If you prefer shorter, more frequent subtitle segments, use `-d` to set a smaller chunk duration.

```bash
qwen3-asr -i "/path/to/my/tech_talk.mp4" -c "Qwen-ASR, DashScope, FFmpeg" -d 60 -srt
```
*This command will try to split the audio into chunks around 60 seconds long, which can result in more granular subtitles.*

#### 6. Run in Silence Mode

Use the `-s` or `--silence` flag to prevent progress details from being printed to the terminal. The final transcript will still be saved to a file.

```bash
qwen3-asr -i "/path/to/my/meeting_recording.m4a" -s
```

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements, please feel free to fork the repo, create a feature branch, and open a pull request. You can also open an issue with the "enhancement" tag.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
