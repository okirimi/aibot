from openai import OpenAI

from src.suisei.adapters.chat import ChatHistory, ChatMessage
from src.suisei.adapters.response import ResponseResult, ResponseStatus
from src.suisei.types import GPTParams
from src.suisei.utils.decorators.error import handle_openai_service_errors

_client = OpenAI()


@handle_openai_service_errors
async def generate_openai_response(
    system_prompt: str,
    prompt: list[ChatMessage],
    model_params: GPTParams,
) -> ResponseResult:
    """Generate a response from the GPT model.

    Parameters
    ----------
    system_prompt : str
        The system instruction.

    prompt : list[ChatMessage]
        A list of chat messages forming the conversation history.

    model_params : GPTModelParams
        Configuration settings for the model, including parameters like
        max_tokens, temperature and top-p sampling.
    """
    convo = ChatHistory(messages=[*prompt, ChatMessage(role="assistant")]).render_message()
    full_prompt = [{"role": "developer", "content": system_prompt}, *convo]
    completion = _client.chat.completions.create(
        # expected loooooooooooooooooong union type
        messages=full_prompt,  # type: ignore[arg-type]
        # specified as app_commands.Choice[int] | str
        model=model_params.model,  # type: ignore[arg-type]
        max_tokens=model_params.max_tokens,
        temperature=model_params.temperature,
        top_p=model_params.top_p,
    )
    openai_response = completion.choices[0].message.content
    return ResponseResult(status=ResponseStatus.SUCCESS, result=openai_response)
