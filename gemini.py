import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
import vertexai.preview.generative_models as generative_models
import json

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

vertexai.init(project="speedy-victory-336109", location="us-central1")
model = GenerativeModel("gemini-1.5-flash-002")

def generate(prompt, generation_config):
    responses = model.generate_content(
        [prompt],
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=False
    )
    return json.loads(responses.text)


def generate_video(prompt, video_path, generation_config):
    with open(video_path, "rb") as f:
        data = f.read()
        video = generative_models.Part.from_data(data, mime_type="video/*")
    
    response = model.generate_content(
      [video, prompt],
      generation_config = generation_config, 
      safety_settings = safety_settings,
      stream = False
    )
    return json.loads(response.text)