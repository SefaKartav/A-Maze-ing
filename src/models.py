"""Pydantic models used by the project.

They validate the input files and describe the output format.
"""

from typing import Any, Literal
from pydantic import BaseModel


class ParameterSpec(BaseModel):
    """The type of one function parameter.

    The type can only be a number, a string or a boolean.
    """

    type: Literal["number", "string", "boolean"]


class FunctionDefinition(BaseModel):
    """One function that the model is allowed to call.

    It holds the name, the description, the parameters and the return type.
    """

    name: str
    description: str
    parameters: dict[str, ParameterSpec]
    returns: ParameterSpec


class PromptTest(BaseModel):
    """One test case from the input file.

    It only holds the prompt written in natural language.
    """

    prompt: str


class FunctionCallResult(BaseModel):
    """The function call that the program builds for one prompt.

    It holds the original prompt, the chosen function name and its arguments.
    """

    prompt: str
    name: str
    parameters: dict[str, Any]
