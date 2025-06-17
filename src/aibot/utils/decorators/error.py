import functools
from collections.abc import Callable
from typing import Any

import anthropic
import openai

from src.aibot.adapters.response import ResponseResult, ResponseStatus
from src.aibot.cli import logger


def handle_anthropic_service_errors(
    func: Callable[..., ResponseResult],
) -> Callable[..., ResponseResult]:
    """Handle errors from Anthropic service functions.

    Catch all exceptions and return the appropriate ResponseResult.

    Parameters
    ----------
    func : Callable
        The function to decorate

    Returns
    -------
    Callable
        The wrapped function
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> ResponseResult:  # noqa: ANN401
        try:
            return await func(*args, **kwargs)
        except (
            anthropic.APIConnectionError,
            anthropic.APITimeoutError,
            anthropic.RateLimitError,
            anthropic.BadRequestError,
            anthropic.AuthenticationError,
            anthropic.PermissionDeniedError,
            anthropic.NotFoundError,
            anthropic.UnprocessableEntityError,
            anthropic.InternalServerError,
            anthropic.APIStatusError,
            anthropic.APIError,
        ) as err:
            error_messages = {
                anthropic.APIConnectionError: "Failed to connect to Anthropic API",
                anthropic.APITimeoutError: "Anthropic API request timed out",
                anthropic.RateLimitError: "Anthropic API rate limit exceeded",
                anthropic.BadRequestError: "Bad request to Anthropic API",
                anthropic.AuthenticationError: "Anthropic API authentication failed",
                anthropic.PermissionDeniedError: "Anthropic API permission denied",
                anthropic.NotFoundError: "Anthropic API resource not found",
                anthropic.UnprocessableEntityError: "Anthropic API unprocessable entity",
                anthropic.InternalServerError: "Anthropic API internal server error",
                anthropic.APIStatusError: (
                    f"Anthropic API status error "
                    f"({err.status_code if hasattr(err, 'status_code') else 'unknown'})"
                ),
                anthropic.APIError: "Anthropic API error",
            }
            msg = f"{error_messages.get(type(err), 'Anthropic API error')}: {err!s}"
            logger.exception(msg)
        except Exception as err:
            msg = f"Unexpected error occurred: {err!s}"
            logger.exception(msg)

        return ResponseResult(status=ResponseStatus.ERROR, result=None)

    return wrapper


def handle_openai_service_errors(
    func: Callable[..., ResponseResult],
) -> Callable[..., ResponseResult]:
    """Handle errors from OpenAI service functions.

    Catch all exceptions and return the appropriate ResponseResult.

    Parameters
    ----------
    func : Callable
        The function to decorate

    Returns
    -------
    Callable
        The wrapped function
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> ResponseResult:  # noqa: ANN401
        try:
            return await func(*args, **kwargs)
        except (
            openai.APIConnectionError,
            openai.APITimeoutError,
            openai.RateLimitError,
            openai.BadRequestError,
            openai.AuthenticationError,
            openai.PermissionDeniedError,
            openai.NotFoundError,
            openai.UnprocessableEntityError,
            openai.InternalServerError,
            openai.APIStatusError,
            openai.APIError,
        ) as err:
            error_messages = {
                openai.APIConnectionError: "Failed to connect to OpenAI API",
                openai.APITimeoutError: "OpenAI API request timed out",
                openai.RateLimitError: "OpenAI API rate limit exceeded",
                openai.BadRequestError: "Bad request to OpenAI API",
                openai.AuthenticationError: "OpenAI API authentication failed",
                openai.PermissionDeniedError: "OpenAI API permission denied",
                openai.NotFoundError: "OpenAI API resource not found",
                openai.UnprocessableEntityError: "OpenAI API unprocessable entity",
                openai.InternalServerError: "OpenAI API internal server error",
                openai.APIStatusError: (
                    f"OpenAI API status error "
                    f"({err.status_code if hasattr(err, 'status_code') else 'unknown'})"
                ),
                openai.APIError: "OpenAI API error",
            }
            msg = f"{error_messages.get(type(err), 'OpenAI API error')}: {err!s}"
            logger.exception(msg)
        except Exception as err:
            msg = f"Unexpected error occurred: {err!s}"
            logger.exception(msg)

        return ResponseResult(status=ResponseStatus.ERROR, result=None)

    return wrapper
