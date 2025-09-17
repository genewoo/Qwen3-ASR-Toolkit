# Qwen3-ASR-Toolkit

[![PyPI version](https://badge.fury.io/py/qwen3-asr-toolkit.svg)](https://badge.fury.io/py/qwen3-asr-toolkit)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An advanced, high-performance Python command-line toolkit for using the **Qwen-ASR API** (formerly Qwen3-ASR-Flash). This implementation overcomes the API's 3-minute audio length limitation by intelligently splitting long audio/video files and processing them in parallel, enabling rapid transcription of hours-long content.

## 🚀 Key Features

-   **Break the 3-Minute Limit**: Seamlessly transcribe audio and video files of any length by bypassing the official API's duration constraint.
-   **Smart Audio Splitting**: Utilizes **Voice Activity Detection (VAD)** to split audio into meaningful chunks at natural silent pauses. This ensures that words and sentences are not awkwardly cut off.
-   **High-Speed Parallel Processing**: Leverages multi-threading to send audio chunks to the Qwen-ASR API concurrently, dramatically reducing the total transcription time for long files.
-   **Automatic Audio Resampling**: Automatically converts audio from any sample rate and channel count to the 16kHz mono format required by the Qwen-ASR API. You can use any audio file without worrying about pre-processing.
-   **Universal Media Support**: Supports virtually any audio and video format (e.g., `.mp4`, `.mov`, `.mkv`, `.mp3`, `.wav`, `.m4a`) thanks to its reliance on FFmpeg.
-   **Simple & Easy to Use**: A straightforward command-line interface allows you to get started with just a single command.

## ⚙️ How It Works

This tool follows a robust pipeline to deliver fast and accurate transcriptions for long-form media:

1.  **Media Loading**: The script first loads your local audio or video file.
2.  **VAD-based Chunking**: It analyzes the audio stream using Voice Activity Detection (VAD) to identify silent segments.
3.  **Intelligent Splitting**: The audio is then split into smaller chunks based on the detected silences. Each chunk is kept under the 3-minute API limit, preventing mid-sentence cuts.
4.  **Parallel API Calls**: A thread pool is initiated to upload and process these chunks concurrently using the DashScope Qwen-ASR API.
5.  **Result Aggregation**: The transcribed text segments from all chunks are collected, re-ordered, and saved.

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

Once installed, you can use the `qwen3-asr` command directly from your terminal.

### Command

```bash
qwen3-asr -i <input_file> [-key <api_key>] [-j <num_threads>] [-v]
```

### Arguments

| Argument              | Short  | Description                                                          | Required/Optional                                |
| --------------------- | ------ | -------------------------------------------------------------------- | ------------------------------------------------ |
| `--input`             | `-i`   | Path to the local audio or video file you want to transcribe.        | **Required**                                     |
| `--dashscope-api-key` | `-key` | Your DashScope API Key.                                              | Optional (if `DASHSCOPE_API_KEY` env var is set) |
| `--num-threads`       | `-j`   | The number of concurrent threads to use for API calls.               | Optional, **Default: 4**                         |
| `--verbose`           | `-v`   | Verbose mode, print detailed information like chunking and progress. | Optional                                         |

### Output

The full transcription result will be printed to the terminal and also saved in a `.txt` file in the same directory as the input file. For example, if you process `my_video.mp4`, the output will be saved to `my_video.txt`.

---

## ✨ Examples

Here are a few examples of how to use the tool.

#### 1. Basic Transcription

Transcribe a video file using the default 4 threads. Assuming you have set the `DASHSCOPE_API_KEY` environment variable.

```bash
qwen3-asr -i "/path/to/my/long_lecture.mp4"
```

#### 2. Transcribe an Audio File with Increased Concurrency

Transcribe a long podcast audio file using 8 parallel threads to speed up the process. This example also shows how to pass the API key directly.

```bash
qwen3-asr -i "/path/to/my/podcast_episode_01.wav" -j 8 -key "your_api_key_here"
```

#### 3. Transcription with Verbose Output

Use the `-v` or `--verbose` flag to see detailed logs during the transcription process, such as audio chunking details and API call status. This is useful for debugging or monitoring progress.

```bash
qwen3-asr -i "/path/to/my/meeting_recording.m4a" -v
```

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements, please feel free to fork the repo, create a feature branch, and open a pull request. You can also open an issue with the "enhancement" tag.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
