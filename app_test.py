import os
import gradio as gr
from azure.identity import ManagedIdentityCredential, get_bearer_token_provider
from openai import AzureOpenAI

AZURE_ENDPOINT = os.environ.get("AZURE_ENDPOINT")
DEPLOYMENT_NAME = os.environ.get("DEPLOYMENT_NAME")
CLIENT_ID = os.environ.get("AZURE_CLIENT_ID")              # only needed for user-assigned identity

credential = ManagedIdentityCredential(client_id=CLIENT_ID) if CLIENT_ID else ManagedIdentityCredential()
token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")

client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    azure_ad_token_provider=token_provider,
    api_version="2024-10-21",
)

def chat(message, history):
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for item in history:
        # Handle both old tuple format and new dict format
        if isinstance(item, dict):
            messages.append({"role": item["role"], "content": item["content"]})
        else:
            user_msg, bot_msg = item
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": bot_msg})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=messages,
    )
    return response.choices[0].message.content

demo = gr.ChatInterface(fn=chat, title="ADEX2 sabdbox Foundry Agent TEST")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
