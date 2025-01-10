from typing import Optional, Dict, Any, List
from avahiplatform.helpers.chats.bedrock_chat import BedrockChat
from Observability import track_observability

class BedrockChatbot:
    def __init__(
        self,
        bedrockchat: BedrockChat,
        max_conversation_turns: int = 10,
        max_message_length: int = 4000
    ):
        """
        Initialize the Chatbot with BedrockChat instance.

        Args:
            bedrockchat (BedrockChat): BedrockChat instance for making API calls.
            max_conversation_turns (int): Maximum number of conversation turns to retain.
            max_message_length (int): Maximum length for each message.
        """
        self.bedrockchat = bedrockchat
        self.conversation_history: List[Dict[str, str]] = []
        self.max_conversation_turns = max_conversation_turns
        self.max_message_length = max_message_length
        self.system_prompt: Optional[str] = None

    def initialize_system(self, system_prompt: str) -> None:
        """
        Initialize the chatbot with a system prompt.

        Args:
            system_prompt (str): The system prompt that defines the chatbot's behavior.
        """
        self.system_prompt = system_prompt[:self.max_message_length]
        self.conversation_history = [{"role": "system", "content": self.system_prompt}]

    def _create_prompt_list(self) -> list:
        """
        Creates a list of prompts for the BedrockChat API based on conversation history.

        Returns:
            list: List containing the formatted prompt for BedrockChat.
        """
        prompt_text = "\n".join(
            f"{turn['role'].capitalize()}: {turn['content']}" for turn in self.conversation_history
        )
        return [{"text": prompt_text}]

    @track_observability
    def chat(
        self,
        user_input: str,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Engage in a chat with the model.

        Args:
            user_input (str): The user's input message.
            stream (bool): Whether to stream the response.

        Returns:
            Dict[str, Any]: Response containing the assistant's reply and metadata.
        """
        if not user_input:
            raise ValueError("Input text cannot be empty.")

        if self.system_prompt is None:
            raise ValueError("System prompt not initialized. Call initialize_system first.")

        user_input = user_input[:self.max_message_length]
        self.conversation_history.append({"role": "user", "content": user_input})

        try:
            prompts = self._create_prompt_list()
            
            if stream:
                response = self.bedrockchat.invoke_stream_parsed(prompts)
            else:
                response = self.bedrockchat.invoke(prompts)

            ai_message = response["response_text"]
            self.conversation_history.append({"role": "assistant", "content": ai_message})

            # Trim conversation history if it exceeds max_conversation_turns
            if len(self.conversation_history) > self.max_conversation_turns * 2:
                # Keep system prompt and last n turns
                self.conversation_history = (
                    [self.conversation_history[0]] +  # System prompt
                    self.conversation_history[-(self.max_conversation_turns * 2 - 1):]  # Last n turns
                )

            return response

        except Exception as e:
            raise

    def get_conversation_history(self) -> str:
        """
        Get the formatted conversation history.

        Returns:
            str: Beautified conversation history.
        """
        beautified_history = "\n".join(
            f"{turn['role'].upper()}: {turn['content']}" for turn in self.conversation_history
        )
        return beautified_history

    def clear_conversation_history(self) -> None:
        """
        Clear the conversation history but maintain the system prompt.
        """
        if self.system_prompt:
            self.conversation_history = [{"role": "system", "content": self.system_prompt}]
        else:
            self.conversation_history.clear()

    def launch_chat_ui(self, share: bool = True):
        """
        Launch the chatbot UI using Gradio with observability tracking
        """
        def send_message(user_input: str, system_prompt: Optional[str], stream: bool) -> str:
            if system_prompt:
                self.initialize_system(system_prompt)
            response = self.chat(user_input, stream=stream)
            return response["response_text"]

        def clear_history():
            self.clear_conversation_history()
            return "Conversation history cleared."

        def get_history() -> str:
            return self.get_conversation_history()

        with gr.Blocks() as demo:
            gr.Markdown("<h1 align='center'>Interactive Chatbot</h1>")
            
            with gr.Row():
                with gr.Column(scale=1):
                    system_prompt_input = gr.Textbox(
                        label="System Prompt",
                        placeholder="Enter system prompt here...",
                        lines=2
                    )
                    chat_input = gr.Textbox(
                        label="User Input",
                        placeholder="Enter your message here...",
                        lines=2
                    )
                    stream_checkbox = gr.Checkbox(label="Stream Response", value=False)
                    
                    with gr.Row():
                        send_button = gr.Button("Send")
                        clear_button = gr.Button("Clear History")
                        history_button = gr.Button("Get History")

                with gr.Column(scale=2):
                    chat_output = gr.Textbox(
                        label="Chatbot Responses",
                        interactive=False,
                        placeholder="Responses will appear here...",
                        lines=5
                    )
                    history_output = gr.Textbox(
                        label="Conversation History",
                        interactive=False,
                        placeholder="History will appear here...",
                        lines=10
                    )

            send_button.click(
                fn=send_message,
                inputs=[chat_input, system_prompt_input, stream_checkbox],
                outputs=[chat_output]
            )
            clear_button.click(
                fn=clear_history,
                inputs=[],
                outputs=[chat_output]
            )
            history_button.click(
                fn=get_history,
                inputs=[],
                outputs=[history_output]
            )

            demo.launch(share=share)
