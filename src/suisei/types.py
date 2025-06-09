from discord import app_commands


class ClaudeParams:
    """Parameters for Claude model."""

    def __init__(
        self,
        model: app_commands.Choice[int] | str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
    ) -> None:
        """Initialize Claude parameters."""
        if model is not None:
            self.model = model
        if max_tokens is not None:
            self.max_tokens = max_tokens
        if temperature is not None:
            self.temperature = temperature
        if top_p is not None:
            self.top_p = top_p

    @property
    def model(self) -> app_commands.Choice[int] | str:
        """Get the model parameter."""
        return self._model

    @model.setter
    def model(self, value: app_commands.Choice[int] | str) -> None:
        """Set and validate model."""
        self._model = value

    @property
    def max_tokens(self) -> int:
        """Get the max_tokens parameter."""
        return self._max_tokens

    @max_tokens.setter
    def max_tokens(self, value: int) -> None:
        """Set and validate max_tokens."""
        if not 1 <= value <= 8192:  # noqa: PLR2004
            msg = "The max_tokens must be between 1 and 8192."
            raise ValueError(msg)
        self._max_tokens = value

    @property
    def temperature(self) -> float:
        """Get the temperature parameter."""
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Set and validate temperature."""
        if not (0.0 <= value <= 1.0):
            msg = "Claude's temperature must be between 0.0 and 1.0."
            raise ValueError(msg)
        self._temperature = value

    @property
    def top_p(self) -> float:
        """Get the top_p parameter."""
        return self._top_p

    @top_p.setter
    def top_p(self, value: float) -> None:
        """Set and validate top_p."""
        if not (0.0 <= value <= 1.0):
            msg = "Claude's top_p must be between 0.0 and 1.0."
            raise ValueError(msg)
        self._top_p = value


class GPTParams:
    """Parameters for GPT model."""

    def __init__(
        self,
        model: app_commands.Choice[int] | str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
        top_p: float | None = None,
    ) -> None:
        """Initialize GPT parameters."""
        if model is not None:
            self.model = model
        if max_tokens is not None:
            self.max_tokens = max_tokens
        if temperature is not None:
            self.temperature = temperature
        if top_p is not None:
            self.top_p = top_p

    @property
    def model(self) -> app_commands.Choice[int] | str:
        """Get the model parameter."""
        return self._model

    @model.setter
    def model(self, value: app_commands.Choice[int] | str) -> None:
        """Set and validate model."""
        self._model = value

    @property
    def max_tokens(self) -> int:
        """Get the max_tokens parameter."""
        return self._max_tokens

    @max_tokens.setter
    def max_tokens(self, value: int) -> None:
        """Set and validate max_tokens."""
        if not 1 <= value <= 8192:  # noqa: PLR2004
            msg = "The max_tokens must be between 1 and 8192."
            raise ValueError(msg)
        self._max_tokens = value

    @property
    def temperature(self) -> float:
        """Get the temperature parameter."""
        return self._temperature

    @temperature.setter
    def temperature(self, value: float) -> None:
        """Set and validate temperature."""
        if not 0.0 <= value <= 2.0:  # noqa: PLR2004
            msg = "The temperature must be between 0.0 and 2.0."
            raise ValueError(msg)
        self._temperature = value

    @property
    def top_p(self) -> float:
        """Get the top_p parameter."""
        return self._top_p

    @top_p.setter
    def top_p(self, value: float) -> None:
        """Set and validate top_p."""
        if not (0.0 <= value <= 1.0):
            msg = "GPT's top_p must be between 0.0 and 1.0."
            raise ValueError(msg)
        self._top_p = value


ParamsType = ClaudeParams | GPTParams
