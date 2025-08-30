import os
import requests
import json
import streamlit as st

class BhashiniPipeline:
    def __init__(self, api_key, user_id, auth_token, endpoint):
        self.headers = {
            "ulcaApiKey": api_key,
            "userID": user_id,
            "Authorization": auth_token,
            "Content-Type": "application/json"
        }
        self.endpoint = endpoint

    def perform_translation(self, source_text, source_lang, target_lang, service_id):
        payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": source_lang,
                            "targetLanguage": target_lang
                        },
                        "serviceId": service_id
                    }
                }
            ],
            "inputData": {
                "input": [{"source": source_text}],
                "audio": [{"audioContent": None}]
            }
        }
        
        response = requests.post(self.endpoint, headers=self.headers, data=json.dumps(payload))
        response_json = response.json()
        if response.status_code == 200:
            translation_output = response_json.get("pipelineResponse", [{}])[0].get("output", [{}])[0].get("target", "")
            return translation_output
        else:
            raise Exception(f"Translation API call failed: {response_json}")

    def run_pipeline(self, source_text, source_lang, target_lang, translate=False):
        translation_output = None
        audio_content = None

        # Translate if requested
        if translate:
            translation_output = self.perform_translation(
                source_text,
                source_lang=source_lang,
                target_lang=target_lang,
                service_id="ai4bharat/indictrans-v2-all-gpu--t4"
            )
        return {
                "translation": translation_output
                  }


# usage example
if __name__ == "__main__":
    # initialize with your credentials and endpoint
    pipeline = BhashiniPipeline(
        api_key=st.secrets["ulca_api_key"],
        user_id=st.secrets["ulca_userid"],
        auth_token=st.secrets["authorization_key"],
        endpoint="https://dhruva-api.bhashini.gov.in/services/inference/pipeline"
    )
    source_text = "This is an example of english to sanskrit translation"
    result = pipeline.run_pipeline(source_text, "en", "sa", translate=True)
    print(result["translation"])
