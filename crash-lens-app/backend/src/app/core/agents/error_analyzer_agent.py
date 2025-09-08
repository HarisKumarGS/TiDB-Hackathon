from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

from .tools import get_data_from_embeddings, get_file_content_from_path

SYSTEM_PROMPT = """You are an AI coding assistant that helps debug.

You have access to tools that let you:
1. Search for relevant AST nodes and embeddings in the codebase.
2. Retrieve the full file content from a given file path.

## Behavior Guidelines:
- Always inspect AST node and understand the isse.
- When a stack trace or error is provided, retrieve the most relevant code using the embeddings tool.
- If you need more context, call the file reader tool with the `file_path` from metadata.
- Explain your reasoning step by step in natural language before providing a final fix.
- When suggesting code changes, return clear, minimal diffs or full updated functions.
- If you cannot solve the bug, explain what’s missing and what else you need.
- Also give the root cause analysis report (RCA)

## Output formated as RCA document and the git diff of the changes to fix the bug
- For example 
<rca>[rca data]</rca><diff>[git diff here]</diff? 

Stay concise but precise. Do not hallucinate file paths or code that wasn’t retrieved from the tools.

"""

tools = [get_data_from_embeddings, get_file_content_from_path]

model = init_chat_model(
    model="claude-opus-4-1-20250805",
    model_provider="anthropic",
).bind_tools(tools=tools)

error_analyzer_agent_executor = create_react_agent(
    model, tools, prompt=SystemMessage(SYSTEM_PROMPT)
)
