import os
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AISearchIndexResource,
    AzureAISearchQueryType,
    AzureAISearchTool,
    AzureAISearchToolResource,
    PromptAgentDefinition,
)

# Replace these with values from YOUR Foundry project.
PROJECT_ENDPOINT = ""
SEARCH_CONNECTION_NAME = ""
SEARCH_INDEX_NAME = ""
MODEL_DEPLOYMENT = "gpt-5"

project = AIProjectClient(
    endpoint=PROJECT_ENDPOINT,
    credential=DefaultAzureCredential(),
)

# This connection must already exist under the Foundry project's
# Connected resources.
connection = project.connections.get(SEARCH_CONNECTION_NAME)
search_tool = AzureAISearchTool(
    azure_ai_search=AzureAISearchToolResource(
        indexes=[
            AISearchIndexResource(
                project_connection_id=connection.id,
                index_name=SEARCH_INDEX_NAME,
                # Start with simple search for the first connectivity test.
                query_type=AzureAISearchQueryType.SIMPLE,
            )
        ]
    )
)

agent = project.agents.create_version(
    agent_name="rag-vm-test",
    definition=PromptAgentDefinition(
        model=MODEL_DEPLOYMENT,
        instructions=(
            "Answer using the Azure AI Search tool. "
            "If the indexed documents do not contain the answer, say so. "
            "Include citations to the retrieved sources."
        ),
        tools=[search_tool],
    ),
    description="VM test of Azure AI Search grounding",
)

print(f"Agent: {agent.name}, version: {agent.version}")

question = "who is Maya Chen"
openai_client = project.get_openai_client()
response = openai_client.responses.create(
    input=question,
    tool_choice="required",
    extra_body={
        "agent_reference": {
            "name": agent.name,
            "type": "agent_reference",
        }
    },
)

print("\nAnswer:\n")
print(response.output_text)