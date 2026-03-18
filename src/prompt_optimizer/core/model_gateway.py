from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Protocol
from urllib import error, request

from prompt_optimizer.core.configuration_models import ExecutionConfiguration
from prompt_optimizer.core.llm_response_parser import (
    ResponseValidationError,
    normalize_structured_improve_response_payload,
)
from prompt_optimizer.core.prompt_module_models import RenderedPrompt
from prompt_optimizer.core.structured_response_models import StructuredImproveResponse


class ModelGatewayError(RuntimeError):
    """Base error for failures raised by model gateway operations."""


class ModelAuthenticationError(ModelGatewayError):
    """Raise when the model API rejects credentials."""


class ModelConnectionError(ModelGatewayError):
    """Raise when the model API cannot be reached reliably."""


class ModelGatewayResponseError(ModelGatewayError):
    """Raise when the model API returns an invalid or unsupported response."""


class TransportConnectionError(RuntimeError):
    """Raise when the low-level HTTP transport cannot complete a request."""


class TransportResponseDecodingError(RuntimeError):
    """Raise when the low-level HTTP transport cannot decode a JSON response."""


@dataclass(frozen=True, slots=True, kw_only=True)
class ModelHttpRequest:
    """Represent an HTTP request issued by the model gateway.

    Attributes:
        url: Target endpoint URL.
        headers: HTTP headers to send with the request.
        body: JSON request body.
    """

    url: str
    headers: dict[str, str]
    body: dict[str, object]

    def __post_init__(self) -> None:
        """Validate required HTTP request fields."""
        if not self.url.strip():
            raise ValueError("url must not be empty.")


@dataclass(frozen=True, slots=True, kw_only=True)
class ModelHttpResponse:
    """Represent an HTTP response returned by the transport.

    Attributes:
        status_code: HTTP status code received from the upstream API.
        body: Parsed JSON response body.
    """

    status_code: int
    body: object

    def __post_init__(self) -> None:
        """Validate response status code range."""
        if self.status_code < 100 or self.status_code > 599:
            raise ValueError("status_code must be a valid HTTP status code.")


class ModelHttpTransport(Protocol):
    """Represent a synchronous JSON HTTP transport used by the model gateway."""

    def send(self, request: ModelHttpRequest) -> ModelHttpResponse:
        """Send a model HTTP request and return the parsed JSON response."""


class ModelGateway(Protocol):
    """Represent the abstract interface for model-backed prompt execution."""

    def generate_structured_improve_response(
        self,
        *,
        rendered_prompt: RenderedPrompt,
        execution_configuration: ExecutionConfiguration,
    ) -> StructuredImproveResponse:
        """Generate a validated structured improvement response."""


@dataclass(slots=True, kw_only=True)
class UrllibModelHttpTransport:
    """Send JSON HTTP requests using Python's standard urllib implementation."""

    timeout_seconds: float = 30.0

    def send(self, request_message: ModelHttpRequest) -> ModelHttpResponse:
        """Send a JSON POST request and parse the JSON response.

        Args:
            request_message: Structured request information from the gateway.

        Returns:
            ModelHttpResponse: Parsed JSON response from the upstream service.

        Raises:
            TransportConnectionError: If the request cannot be completed.
            TransportResponseDecodingError: If the response body is not valid JSON.
        """
        request_body = json.dumps(request_message.body).encode("utf-8")
        http_request = request.Request(
            url=request_message.url,
            data=request_body,
            headers={
                **request_message.headers,
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(http_request, timeout=self.timeout_seconds) as http_response:
                response_text = http_response.read().decode("utf-8")
                return ModelHttpResponse(
                    status_code=http_response.getcode(),
                    body=_load_json_response_body(response_text),
                )
        except error.HTTPError as http_error:
            response_text = http_error.read().decode("utf-8", errors="replace")
            return ModelHttpResponse(
                status_code=http_error.code,
                body=_load_json_error_body(response_text),
            )
        except error.URLError as transport_error:
            raise TransportConnectionError(str(transport_error.reason)) from transport_error
        except OSError as transport_error:
            raise TransportConnectionError(str(transport_error)) from transport_error


@dataclass(slots=True, kw_only=True)
class OpenAiCompatibleModelGateway:
    """Call an OpenAI-compatible chat completion API for prompt improvement."""

    base_url: str
    api_key: str
    transport: ModelHttpTransport = field(default_factory=UrllibModelHttpTransport)

    def __post_init__(self) -> None:
        """Validate gateway connection settings after construction."""
        if not self.base_url.strip():
            raise ValueError("base_url must not be empty.")
        if not self.api_key.strip():
            raise ValueError("api_key must not be empty.")

    def generate_structured_improve_response(
        self,
        *,
        rendered_prompt: RenderedPrompt,
        execution_configuration: ExecutionConfiguration,
    ) -> StructuredImproveResponse:
        """Call the configured model and return a validated structured response.

        Args:
            rendered_prompt: Rendered prompt text produced by a prompt module.
            execution_configuration: Runtime model and formatting options.

        Returns:
            StructuredImproveResponse: Parsed and validated model output.

        Raises:
            ModelAuthenticationError: If upstream authentication fails.
            ModelConnectionError: If the upstream service cannot be reached.
            ModelGatewayResponseError: If the upstream response is malformed.
        """
        if execution_configuration.model_name is None:
            raise ModelGatewayResponseError("execution_configuration.model_name is required.")

        request_message = ModelHttpRequest(
            url=self.base_url.rstrip("/") + "/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            body={
                "model": execution_configuration.model_name,
                "messages": [
                    {
                        "role": "user",
                        "content": _build_request_message(
                            rendered_prompt=rendered_prompt,
                            execution_configuration=execution_configuration,
                        ),
                    }
                ],
                "response_format": {"type": "json_object"},
            },
        )

        try:
            response_message = self.transport.send(request_message)
        except TransportConnectionError as error:
            raise ModelConnectionError("Unable to reach model API.") from error
        except TransportResponseDecodingError as error:
            raise ModelGatewayResponseError("Model API did not return valid JSON.") from error

        if response_message.status_code in {401, 403}:
            raise ModelAuthenticationError("Authentication failed for model API.")
        if response_message.status_code >= 400:
            raise ModelGatewayResponseError(
                f"Model API request failed with status code {response_message.status_code}."
            )

        response_payload = _extract_structured_response_payload(response_message.body)
        try:
            return normalize_structured_improve_response_payload(response_payload)
        except ResponseValidationError as error:
            raise ModelGatewayResponseError(str(error)) from error


def _build_request_message(
    *,
    rendered_prompt: RenderedPrompt,
    execution_configuration: ExecutionConfiguration,
) -> str:
    execution_directives = [
        "Return a JSON object with fields: judgment, reason, improvedPrompt, changes.",
        f"allowNoChange={str(execution_configuration.allow_no_change).lower()}",
        f"strictMinimalEdit={str(execution_configuration.strict_minimal_edit).lower()}",
        f"preferShort={str(execution_configuration.prefer_short).lower()}",
        f"outputFormat={execution_configuration.output_format.value}",
    ]
    return (
        rendered_prompt.prompt_text.strip()
        + "\n\nExecution Configuration:\n- "
        + "\n- ".join(execution_directives)
    )


def _extract_structured_response_payload(response_body: object) -> object:
    if not isinstance(response_body, dict):
        raise ModelGatewayResponseError("Model API response must be a JSON object.")

    raw_choices = response_body.get("choices")
    if not isinstance(raw_choices, list) or not raw_choices:
        raise ModelGatewayResponseError("Model API response must contain choices[0].")

    first_choice = raw_choices[0]
    if not isinstance(first_choice, dict):
        raise ModelGatewayResponseError("Model API choices[0] must be an object.")

    raw_message = first_choice.get("message")
    if not isinstance(raw_message, dict):
        raise ModelGatewayResponseError("Model API response must contain message content.")

    raw_content = raw_message.get("content")
    if not isinstance(raw_content, str) or not raw_content.strip():
        raise ModelGatewayResponseError("Model API message content must be a non-empty string.")

    try:
        return json.loads(raw_content)
    except json.JSONDecodeError as error:
        raise ModelGatewayResponseError("Model API message content must be valid JSON.") from error


def _load_json_response_body(response_text: str) -> object:
    try:
        return json.loads(response_text)
    except json.JSONDecodeError as error:
        raise TransportResponseDecodingError("Response body must be valid JSON.") from error


def _load_json_error_body(response_text: str) -> object:
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {"error": {"message": response_text}}
