"""AI Management module for the NetSourceAI chatbot.
This module handles all AI-related functionality including model initialization,
conversation management, and tool calls processing.
"""

from openai import OpenAI
from tools_management import Tools_Class
from typing import Dict, Any, List
import json
import yaml

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

class Ai_Management:
    """Class responsible for managing AI interactions and conversation flow.
    
    This class handles the interaction with the AI model, including chat completions,
    tool calls processing, and conversation history management.
    
    Attributes:
        config (Dict[str, Any]): Application configuration
        model (str): Name of the AI model to use
        client (OpenAI): OpenAI API client instance
        temperature (float): Response temperature for model generation
        tools (Tools_Class): Tools management instance
        ai_tools (List[Dict]): Available tool definitions
        history (List[Dict]): Conversation history
    """
    
    def __init__(self):
        """Initialize all AI components and configurations."""
        self._load_configuration()
        self._setup_client()
        self._initialize_conversation()
        self._setup_tools()
    
    def _load_configuration(self) -> None:
        """Load and set up configuration parameters."""
        self.config = load_config()
        self.model = self.config["model"]["name"]
        self.temperature = self.config["model"]["default_temperature"]
    
    def _setup_client(self) -> None:
        """Initialize the OpenAI client with configuration."""
        self.client = OpenAI(
            base_url=self.config["model"]["base_url"],
            api_key=self.config["model"]["api_key"]
        )
    
    def _initialize_conversation(self) -> None:
        """Initialize conversation history with system prompt."""
        self.system_prompt = [
            {"role": "system", "content": self.config["system_prompt"]}
        ]
        self.history = self.system_prompt
    
    def _setup_tools(self) -> None:
        """Initialize tools management system."""
        self.tools = Tools_Class()
        self.ai_tools = self.tools.ai_tools
    
    # --- Message Processing Methods ---
    
    def generation_loop(self, message: str) -> str:
        """Main processing loop for generating AI responses.
        
        Args:
            message (str): User input message
            
        Returns:
            str: AI generated response
        """
        # Adds user message to history
        self.history.append({"role": "user", "content": str(message)})
        # Gets AI response
        print("AI is thinking...")
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            tools=self.ai_tools,
            temperature=self.temperature,
        )
        
        if response.choices[0].message.tool_calls:
            print("Tool call received and being processed")
            # Extract tool calls from the response
            tool_calls = response.choices[0].message.tool_calls
            # Add tool calls to history
            self._add_tool_calls_to_history(tool_calls)
            # Process each tool call
            self._process_tool_calls(tool_calls)
            # Returns final response
            return self._generate_final_response()
        else:
            content = response.choices[0].message.content
            print(content)
            # Adds AI response to history
            self.history.append({"role": "assistant", "content": content})
            # Returns final response
            return content
    
    # --- Final Response Generation ---
    
    def _generate_final_response(self) -> str:
        """Generate final response after tool calls.
        
        Returns:
            str: Final AI response
        """
        # Stream the AI response
        print("AI is thinking...")
        stream_response = self.client.chat.completions.create(
            model=self.model,
            messages=self.history,
            stream=True
        )
        
        # Process the streamed response
        ai_output = ""
        for chunk in stream_response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                ai_output += content
        
        # Add the final AI output to history
        self.history.append({"role": "assistant", "content": ai_output})
        print("\n"*2)
        
        return ai_output
    
    # --- Tool Calls Processing ---
    
    def _add_tool_calls_to_history(self, tool_calls: List[Any]) -> None:
        """Add tool calls to conversation history.
        
        Args:
            tool_calls: List of tool calls from AI response
        """
        tool_call_from_ai = {
            "role": "assistant",
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": tool_call.function,
                }
                for tool_call in tool_calls
            ],
        }
        # Add tool call to history
        self.history.append(tool_call_from_ai)
    
    def _process_tool_calls(self, tool_calls: List[Any]) -> None:
        """Process each tool call and add results to history.
        
        Args:
            tool_calls: List of tool calls to process
        """
        for tool_call in tool_calls:
            # Extract tool call name
            name_function = tool_call.function.name
            try:
                # Extract arguments from tool call
                args = json.loads(tool_call.function.arguments)
            except Exception as e:
                print(f"Error retrieving arguments: {e}")
                args = {}
            
            # Execute the tool call based on its name
            if name_function == "fetch_wikipedia_information":
                result = self.tools.fetch_wikipedia_information(args["wikipedia_query"])
            elif name_function == "fetch_internet_information":
                result = self.tools.fetch_internet_information(args["query"])
            elif name_function == "get_current_date_and_time":
                result = self.tools.get_current_date_and_time()
            else:
                result = "Error: not all variables have been provided."
            
            # Add result to history
            print(result)
            self.history.append({
                "role": "tool",
                "content": json.dumps({"status": "success", "message": result}),
                "tool_call_id": tool_call.id,
            })
    