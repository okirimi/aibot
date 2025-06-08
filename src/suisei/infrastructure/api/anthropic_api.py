import anthropic

from src.suisei.adapters.chat import ChatHistory, ChatMessage
from src.suisei.adapters.response import ResponseResult, ResponseStatus
from src.suisei.cli import logger
from src.suisei.types import ClaudeParams
from src.suisei.utils.decorators.error import handle_anthropic_service_errors

_client = anthropic.Anthropic()


@handle_anthropic_service_errors
async def generate_anthropic_response(
    prompt: list[ChatMessage],
    model_params: ClaudeParams,
    system_prompt: str,
) -> ResponseResult:
    """Generate a response from the Anthropic API."""
    convo = ChatHistory(messages=[*prompt, ChatMessage(role="assistant")]).render_message()
    response = _client.messages.create(
        # specified as app_commands.Choice[int] | str
        model=model_params.model,  # type: ignore[arg-type]
        # specified as list[ChatMessage]
        messages=convo,  # type: ignore[arg-type]
        max_tokens=model_params.max_tokens,
        system=system_prompt,
        temperature=model_params.temperature,
        top_p=model_params.top_p,
    )
    if response.content[0].type == "text":
        claude_response = response.content[0].text
    logger.info("Successfully generated response from Anthropic API")

    return ResponseResult(status=ResponseStatus.SUCCESS, result=claude_response)
