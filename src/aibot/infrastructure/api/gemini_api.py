from google import genai
from google.genai import types

from src.aibot.adapters.chat import ChatHistory, ChatMessage
from src.aibot.adapters.response import ResponseResult, ResponseStatus
from src.aibot.types import GeminiParams

_client = genai.Client()


async def generate_gemini_response(
    prompt: list[ChatMessage],
    model_params: GeminiParams,
    system_prompt: str,
) -> ResponseResult:
    """Generate a response from the Gemini API."""
    convo = ChatHistory(messages=[*prompt, ChatMessage(role="assistant")]).render_message()
    contents = "\n".join([msg["content"] for msg in convo if msg["content"]])
    response = _client.models.generate_content(
        model=model_params.model,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=model_params.temperature,
            top_p=model_params.top_p,
        ),
        contents=contents,
    )

    return ResponseResult(status=ResponseStatus.SUCCESS, result=response.text)
