import os
import time
import random
import dashscope

from pydub import AudioSegment


MAX_API_RETRY = 10
API_RETRY_SLEEP = (1, 2)


class QwenASR:
    def __init__(self, model="qwen3-asr-flash"):
        self.model = model

    def asr(self, wav_url: str, context=""):
        if not wav_url.startswith("http"):
            assert os.path.exists(wav_url), f"{wav_url} not exists!"
            file_path = wav_url
            file_size = os.path.getsize(file_path)

            # file size > 10M
            if file_size > 10 * 1024 * 1024:
                # convert to mp3
                mp3_path = os.path.splitext(file_path)[0] + ".mp3"
                audio = AudioSegment.from_file(file_path)
                audio.export(mp3_path, format="mp3")
                wav_url = mp3_path

            wav_url = f"file://{wav_url}"

        # Submit the ASR task
        for _ in range(MAX_API_RETRY):
            try:
                messages = [
                    {
                        "role": "system",
                        "content": [
                            {"text": context},
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            {"audio": wav_url},
                        ]
                    }
                ]
                response = dashscope.MultiModalConversation.call(
                    model=self.model,
                    messages=messages,
                    result_format="message",
                    asr_options={
                        "enable_lid": True,
                        "enable_itn": False
                    }
                )
                if response.status_code != 200:
                    raise Exception(f"http status_code: {response.status_code} {response}")
                output = response['output']['choices'][0]
                if output['finish_reason'] not in ('stop', 'function_call'):
                    print(f'{self.model} finish with error...\n{response}')
                    break
                recog_text = output["message"]["content"][0]["text"]
                return recog_text
            except Exception as e:
                print(f"Retry {_ + 1}...  {wav_url}\n{response}")
                if response.code == "DataInspectionFailed":
                    break
            time.sleep(random.uniform(*API_RETRY_SLEEP))
        raise Exception(f"{wav_url} task failed!\n{response}")


if __name__ == "__main__":
    qwen_asr = QwenASR(model="qwen3-asr-flash")
    asr_text = qwen_asr.asr(wav_url="/path/to/your/wav_file.wav")
    print(asr_text)
