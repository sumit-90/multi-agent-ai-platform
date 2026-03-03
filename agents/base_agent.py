from abc import ABC, abstractmethod
from typing import Any
import logging


class BaseAgent(ABC):
    def __init__(self, name: str, role: str, llm_client: Any, prompt: str):
        self.name = name
        self.role = role
        self.llm_client = llm_client
        self.tools: dict[str, Any] = {}
        self.prompt = prompt
        self.logger = logging.getLogger(f"agent.{self.name}")

    @abstractmethod
    def process_input(self, task: str, **kwargs: Any) -> str:
        """Process the input task and return any necessary data for execution."""


    def run(self, task: str, **kwargs: Any) -> str:
        """Execute the agent for the given task and return a structured response."""
        try:
            self.logger.info(f"Running agent '{self.name}' for task: {task}")
            prompt = self.process_input(task, **kwargs)   # returns ready prompt
            response = self.call_llm(prompt)
            self.logger.info(f"Agent '{self.name}' completed task successfully")
            self.logger.debug(f"Agent '{self.name}' response: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Error occurred while running agent: {e}")
            raise ValueError(f"Error occurred while running agent '{self.name}'") from e

    def register_tool(self, tool: Any) -> None:
        if not hasattr(tool, 'name'):
            raise AttributeError(f"Tool must have a 'name' attribute")
        if tool.name in self.tools:
            self.logger.warning(f"Tool '{tool.name}' already registered, overwriting")
        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool '{tool.name}' for agent '{self.name}'")

    def execute_tool(self, tool_name: str, **kwargs: Any) -> Any:
        """Execute a registered tool by name with the given arguments."""
        try:
            if tool_name not in self.tools:
                raise KeyError(f"Tool '{tool_name}' not found")
            return self.tools[tool_name].execute(**kwargs)
        except Exception as e:
            self.logger.error(f"Error occurred while executing tool: {e}")
            raise ValueError(f"Error occurred while executing tool '{tool_name}' for agent '{self.name}'") from e


    def call_llm(self, prompt: str) -> str:
        """Call the LLM client with the given prompt and return the response."""
        try:
            if self.llm_client is None:
                raise ValueError("LLM client is not set for this agent.")
            return self.llm_client.generate(prompt)
        except Exception as e:
            self.logger.error(f"Error occurred while calling LLM: {e}")
            raise ValueError(f"Error occurred while calling LLM for agent '{self.name}'") from e
    

    def list_tools(self) -> list[str]:
        """Return names of all registered tools."""
        return list(self.tools.keys())
    
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"role={self.role!r}, "
            f"tools={list(self.tools.keys())})"
        )