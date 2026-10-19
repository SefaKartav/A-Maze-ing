"""Pydantic models used by the project.

They validate the input files and describe the output format.
"""

from typing import Any
from pydantic import BaseModel


class ParameterSpec(BaseModel):
    """The type of one function parameter.

    Any type name is accepted when the file is loaded. Unsupported
    types are reported later, only for the prompts that need them.
    """

    type: str


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
