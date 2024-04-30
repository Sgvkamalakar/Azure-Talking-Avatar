import streamlit as st
import requests
import json
from urllib.parse import unquote
import time
import logging
from dotenv import load_dotenv
import os
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p %Z")
logger = logging.getLogger(__name__)

load_dotenv()
SUBSCRIPTION_KEY = os.getenv('SUBSCRIPTION_KEY')
SERVICE_REGION = os.getenv('SERVICE_REGION')

st.set_page_config(page_title="Talking Avatar", page_icon="🗣️",initial_sidebar_state="auto",layout='centered')
NAME = "Text-to-Speech"
DESCRIPTION = "Using Azure AI Services"

lang_voices = {
    'Arabic': ['ar-SA', 'ar-SA-ZariyahNeural'],
    'Bahasa Indonesian': ['id-ID', 'id-ID-GadisNeural'],
    'Bengali': ['bn-IN', 'bn-IN-TanishaaNeural'],
    'Chinese Mandarin': ['zh-CN', 'zh-CN-XiaoxiaoNeural'],
    'Dutch': ['nl-NL', 'nl-NL-FennaNeural'],
    'English': ['en-US', 'en-US-AvaNeural'],
    'French': ['fr-FR', 'fr-FR-DeniseNeural'],
    'German': ['de-DE', 'de-DE-KatjaNeural'],
    'Hindi': ['hi-IN', 'hi-IN-SwaraNeural'],
    'Italian': ['it-IT', 'it-IT-ElsaNeural'],
    'Japanese': ['ja-JP', 'ja-JP-NanamiNeural'],
    'Korean': ['ko-KR', 'ko-KR-SunHiNeural'],
    'Russian': ['ru-RU', 'ru-RU-SvetlanaNeural'],
    'Spanish': ['es-ES', 'es-ES-ElviraNeural'],
    'Telugu': ['te-IN', 'te-IN-ShrutiNeural']
}

with st.sidebar:
    st.markdown("[Source Code](https://github.com/Sgvkamalakar/Azure-Talking-Avatar)")
    st.markdown("[Explore my Codes](https://github.com/sgvkamalakar)")
    st.markdown("[Connect with me on LinkedIn](https://www.linkedin.com/in/sgvkamlakar)")
    st.markdown("Learn more about Text-to-Speech Avatar on Microsoft Azure [here](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech-avatar/what-is-text-to-speech-avatar)")
    st.markdown("Developed with 💓 by Kamalakar")
    
def submit_synthesis(text,voice,style):
    url = f'https://{SERVICE_REGION}.{SERVICE_HOST}/api/texttospeech/3.1-preview1/batchsynthesis/talkingavatar'
    header = {
        'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY,
        'Content-Type':'application/json'
    }
    payload = {
        'displayName': NAME,
        'description': DESCRIPTION,
        "textType": "PlainText",
        'synthesisConfig': {
            "voice": voice,
        },
        'customVoices': {},
        "inputs": [
            {
                "text": text,
            },
        ],
        "properties": {
            "customized": False,
            "talkingAvatarCharacter": "lisa",
            "talkingAvatarStyle": style,
            "videoFormat": "webm",
            "videoCodec": "vp9",
            "subtitleType": "soft_embedded",
            "backgroundColor": "transparent",
        }
    }

    response = requests.post(url, json.dumps(payload), headers=header)
    if response.status_code < 400:
        logger.info('Batch avatar synthesis job submitted successfully')
        logger.info(f'Job ID: {response.json()["id"]}')
        return response.json()["id"]
    else:
        logger.error(f'Failed to submit batch avatar synthesis job: {response.text}')
        return None

def get_content_from_url(decoded_url):
    try:
        response = requests.get(decoded_url)
        if response.status_code == 200:
            return response.content  # Return the content of the response
        else:
            return f"Error: Unable to retrieve content from URL. Status code: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"
    
def get_synthesis(job_id):
    url = f'https://{SERVICE_REGION}.{SERVICE_HOST}/api/texttospeech/3.1-preview1/batchsynthesis/talkingavatar/{job_id}'
    header = {
        'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY
    }
    response = requests.get(url, headers=header)
    if response.status_code < 400:
        logger.debug('Get batch synthesis job successfully')
        logger.debug(response.json())
        if response.json()['status'] == 'Succeeded':
            logger.info(f'Batch synthesis job succeeded. Download URL: {response.json()["outputs"]["result"]}')
            video_url = response.json()["outputs"]["result"]
            decoded_url = unquote(video_url)
            con=get_content_from_url(decoded_url)
            if len(con)<100:
                st.error("An error occurred while processing the request. Please try again later 😢")
                return 0
            else:
                st.markdown(f"You can download the synthesized avatar video [here]({decoded_url}).")
                st.video(decoded_url)
                return 1

    else:
        logger.error(f'Failed to get batch synthesis job: {response.text}')

def list_synthesis_jobs(skip: int = 0, top: int = 100):
    url = f'https://{SERVICE_REGION}.customvoice.api.speech.microsoft.com/api/texttospeech/3.1-preview1/batchsynthesis/talkingavatar?skip={skip}&top={top}'
    header = {
        'Ocp-Apim-Subscription-Key': SUBSCRIPTION_KEY
    }
    response = requests.get(url, headers=header)
    if response.status_code < 400:
        logger.info(f'List batch synthesis jobs successfully, got {len(response.json()["values"])} jobs')
        logger.info(response.json())
    else:
        logger.error(f'Failed to list batch synthesis jobs: {response.text}')


def main():
    
    st.title("Azure Text-to-Talking Avatar")
    
    col1,col2=st.columns(2)
    with col1:
        lang=st.selectbox('Choose the language',list(lang_voices.keys()), index=5) 
    with col2:
        style=st.selectbox('Avatar Style',["Casual-Sitting","Graceful-Sitting","Technical-Sitting","Graceful-Standing","Technical-Standing"],index=1)
    style=style.lower()
    voice=lang_voices[lang][1]
    text_input = st.text_area(f'Type text in {lang}')
    submit_button = st.button("Submit Job")
    st.error("The resource group associated with this project has been deactivated, resulting in the current non-functionality of the app 🤧... I apologize for any inconvenience caused 😔...")
    st.info("If you require further assistance or have any questions, feel free to reach out to me at sgvkamalakar@gmail.com")
    if submit_button:
        if text_input.strip()!='':
            with st.spinner("Processing..."):
                job_id = submit_synthesis(text_input,voice,style)
                if job_id is not None:
                    while True:
                        status = get_synthesis(job_id)
                        if status == 1:
                            st.success('Batch avatar synthesis job succeeded ✅')
                            break
                        elif status == 0:
                            st.error('Uh-oh! The avatar synthesis job took an unexpected turn. ❌')
                            break
                        else:
                            time.sleep(5)
        else:
            st.info("Give me something to work with! How about a dazzling sentence? 😄")
            
if __name__ == '__main__':
    main()

