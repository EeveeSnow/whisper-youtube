import torch
from multiprocessing.pool import ThreadPool
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import asyncio
import websockets
from pytube import YouTube
from datetime import timedelta
from googletrans import Translator, constants
import os


translator = Translator()


device = "cuda"
torch_dtype = torch.float16 

model_id = "openai/whisper-large-v3"
# model_id = "Vickyee/whisper-small-ja"




model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    max_new_tokens=128,
    chunk_length_s=10,
    batch_size=16,
    return_timestamps=True,
    torch_dtype=torch_dtype,
    device=device,
)




def video(link, audio_file):
    video_file = YouTube(link).streams.filter(file_extension='mp4').order_by('resolution').desc().first().download()
    video_file = video_file.split("\\")[-1]
    # os.system(f'ffmpeg -i "{video_file}" -i "{audio_file}" -map 0:v -map 1:a -c:v copy -shortest "out_{video_file}"')
    return f"{video_file}"

def captioning(link, audio_file):
    result = pipe(audio_file, return_timestamps=True, generate_kwargs={"task": "translate"})['chunks']
    translation(result, audio_file)
    return f"{audio_file.split('.')[0]}.srt"

def translation(result, audio_file):
    lines = ["WEBVTT\n\n"]
    c = 1
    for n in range(len(result)):
        if 'Translation by' not in result[n]['text']:
            if result[n]['timestamp'][1] != None:
                lines.append(f"{c}\n0{timedelta(seconds=int(result[n]['timestamp'][0]))}.000 --> 0{timedelta(seconds=int(result[n]['timestamp'][1]))}.000\n{result[n]['text']}\n\n")
                # lines.append(f"{c}\n0{timedelta(seconds=int(result[n]['timestamp'][0]))}.000 --> 0{timedelta(seconds=int(result[n]['timestamp'][1]))}.000\n{translator.translate(result[n]['text'], dest='en').text}\n\n")
                c += 1
    save(lines, audio_file)
    return None

def save(lines, audio_file):
    subs = open(f"{audio_file.split('.')[0]}.vtt", "w")
    subs.writelines(lines)
    subs.close()

async def caption(websocket):
    while True:
        pool_v = ThreadPool(processes=1)
        pool_c = ThreadPool(processes=1)
        link = await websocket.recv()
        # await websocket.send("getting data")
        audio_file = YouTube(link).streams.filter(audio_codec="opus",only_audio=True).order_by('abr').desc().first().download()
        audio_file = audio_file.split("\\")[-1]
        # await websocket.send("processing data")
        video(link, audio_file)
        captioning(link, audio_file)
        # await websocket.send("video processed")
        # await websocket.send("audio processed")
        await websocket.send(f"{audio_file.split('.')[0]}")
        

        
async def main():
    async with websockets.serve(caption, "localhost", 8765, max_size=2**32):
        await asyncio.Future()  # run forever




if __name__ == "__main__":
    asyncio.run(main())