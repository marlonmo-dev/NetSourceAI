"""Main application file for the NetSourceAI chatbot interface."""

import streamlit as st
from ai_management import Ai_Management
from typing import Dict, Any
import yaml

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml"""
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

class GUI:
    """Main graphical interface for the NetSourceAI application.
    
    This class manages the entire Streamlit user interface, 
    including initialization, configuration, and user interactions.
    
    Attributes:
        config (Dict[str, Any]): Application configuration
        ai_chat (Ai_Management): AI interaction manager
    """
    
    def __init__(self):
        """Initialize the GUI application."""
        self._initialize_app()
        self._render_interface()
    
    # --- Initialization Methods ---
    
    def _initialize_app(self) -> None:
        """Initialize application components."""
        self.config = load_config()
        self._setup_page_config()
        self._initialize_session_state()
        self.ai_chat = Ai_Management()
    
    def _setup_page_config(self) -> None:
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title=self.config["ui"]["page_title"],
            page_icon=self.config["ui"]["page_icon"]
        )
    
    def _initialize_session_state(self) -> None:
        """Initialize or reset session state variables."""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'speech_enabled' not in st.session_state:
            st.session_state.speech_enabled = self.config["ui"]["sound_enabled"]
    
    # --- Interface Rendering Methods ---
    
    def _render_interface(self) -> None:
        """Render the main application interface."""
        self.ai_chat.temperature = self._render_sidebar()
        self._render_main_container()
    
    def _render_sidebar(self) -> float:
        """Render the settings sidebar.
        
        Returns:
            float: Selected temperature value
        """
        with st.sidebar:
            st.title("⚙️ Settings")
            
            temperature = st.slider(
                "🔥 Response Temperature",
                min_value=0.0,
                max_value=1.0,
                value=self.config["model"]["default_temperature"],
                step=0.1
            )

            st.session_state.speech_enabled = st.toggle("🔊 Voice Output", value=st.session_state.speech_enabled)
            
            if st.button("🗑️ Clear history"):
                self._clear_chat_history()
            
            return temperature
    
    def _render_main_container(self) -> None:
        """Render the main chat interface container."""
        with st.container():
            st.title(self.config["ui"]["app_title"])
            st.markdown("---")
            
            self._render_chat_messages()
            self._handle_user_input()
    
    # --- Chat Management Methods ---
    
    def _render_chat_messages(self) -> None:
        """Display the chat message history."""
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
    
    def _handle_user_input(self) -> None:
        """Handle user input and chat response."""
        user_input = st.chat_input(
            placeholder="Write your message here...",
            key="user_input"
        )
        
        if user_input:
            self._process_chat_response(user_input)
    
    def _process_chat_response(self, user_input: str) -> None:
        """Process chat response and update session state.
        
        Args:
            user_input (str): User's message
        """
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        with st.spinner("💭 Research in progress..."):
            response = self.ai_chat.generation_loop(user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.rerun()
    
    def _clear_chat_history(self) -> None:
        """Clear chat history and reset state."""
        st.session_state.messages = []
        self.ai_chat.history = self.ai_chat.system_prompt
        st.rerun()

# Application entry point
if __name__ == "__main__":
    GUI()