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

def chat(message, history, request: gr.Request):
    username = request.headers.get("x-ms-client-principal-name", "unknown")
    print(f"User: {username}, Message: {message}")  # shows in Container App logs
    
    # rest of your chat function...
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    for item in history:
        if isinstance(item, dict):
            # Gradio 4.x dict format
            if item.get("content") is not None:
                messages.append({"role": item["role"], "content": item["content"]})
        else:
            # Old tuple format
            user_msg, bot_msg = item
            if user_msg is not None:
                messages.append({"role": "user", "content": user_msg})
            if bot_msg is not None:
                messages.append({"role": "assistant", "content": bot_msg})
    messages.append({"role": "user", "content": message})

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=messages,
    )
    return response.choices[0].message.content

demo = gr.ChatInterface(fn=chat, title="ADEX2 Sabdbox Foundry Agent TEST")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
