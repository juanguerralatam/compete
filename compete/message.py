# Copyright (c) Harbin Institute of Technology.
# Licensed under the MIT License.
#
# Source Attribution:
# The majority of this code is derived from the following sources:
# - Chatarena GitHub Repository: https://github.com/Farama-Foundation/chatarena

from typing import List, Union
from dataclasses import dataclass
import time
from uuid import uuid1
import hashlib

# Preserved roles
SYSTEM_NAME = "System"
MODERATOR_NAME = "Moderator"

def _hash(input: str):
    """
    Helper function that generates a SHA256 hash of a given input string.

    Parameters:
        input (str): The input string to be hashed.

    Returns:
        str: The SHA256 hash of the input string.
    """
    hex_dig = hashlib.sha256(input.encode()).hexdigest()
    return hex_dig


@dataclass
class Message:
    """
    Represents a message in the chatArena environment.

    Attributes:
        agent_name (str): Name of the agent who sent the message.
        content (str): Content of the message.
        summary (str): Summary of the message. Defaults to None.
        turn (int): The turn at which the message was sent.
        timestamp (int): Wall time at which the message was sent. Defaults to current time in nanoseconds.
        visible_to (Union[str, List[str]]): The receivers of the message. Can be a single agent, multiple agents, or 'all'. Defaults to 'all'.
        msg_type (str): Type of the message, e.g., 'text'. Defaults to 'text'.
        logged (bool): Whether the message is logged in the database. Defaults to False.
    """
    agent_name: str
    content: str
    turn: int
    timestamp: int = time.time_ns()
    visible_to: Union[str, List[str]] = 'all'
    msg_type: str = "text"
    logged: bool = False  # Whether the message is logged in the database

    @property
    def msg_hash(self):
        # Generate a unique message id given the content, timestamp and role
        return _hash(
            f"agent: {self.agent_name}\ncontent: {self.content}\ntimestamp: {str(self.timestamp)}\nturn: {self.turn}\nmsg_type: {self.msg_type}")

class MessagePool():
    """
    A pool to manage the messages in the chatArena environment.

    The pool is essentially a list of messages, and it allows a unified treatment of the visibility of the messages.
    It supports two configurations for step definition: multiple players can act in the same turn (like in rock-paper-scissors).
    Agents can only see the messages that 1) were sent before the current turn, and 2) are visible to the current role.
    """
    
    def __init__(self, log_path: str = None):
        """
        Initialize the MessagePool with a unique conversation ID.
        """
        self.conversation_id = str(uuid1())
        self._messages: List[Message] = []  # TODO: for the sake of thread safety, use a queue instead
        self._last_message_idx = 0
        self.log_file = open(log_path, "a") if log_path else None
        
    def reset(self):
        """
        Clear the message pool.
        """
        self._messages = []
        
    def append_message(self, message: Message):
        """
        Append a message to the pool.

        Parameters:
            message (Message): The message to be added to the pool.
        """
        self._messages.append(message)
        print(f"[{message.agent_name}->{message.visible_to}]: {message.content}")
        self.log_file.write(f"[{message.agent_name}->{message.visible_to}]: {message.content}\n\n")

    def print(self):
        """
        Print all the messages in the pool.
        """
        for message in self._messages:
            print(f"[{message.agent_name}->{message.visible_to}]: {message.content}")

    def remove_role_messages(self, role: str):
        """
        Remove all the messages sent by a given role.

        Parameters:
            role (str): The role whose messages will be removed.
        """
        self._messages = [message for message in self._messages if message.agent_name != role]

    @property
    def last_turn(self):
        """
        Get the turn of the last message in the pool.

        Returns:
            int: The turn of the last message.
        """
        if len(self._messages) == 0:
            return 0
        else:
            return self._messages[-1].turn

    def compress_last_turn(self, summary: Message):
        """
        Summarize the messages sent before a given turn.

        Parameters:
            turn (int): The given turn.
        """
        last_turn = summary.turn
        self._messages = [message for message in self._messages if message.turn < last_turn]
        self._messages.append(summary)

    @property
    def last_message(self):
        """
        Get the last message in the pool.

        Returns:
            Message: The last message.
        """
        if len(self._messages) == 0:
            return None
        else:
            return self._messages[-1]
    
    def get_last_message_system_to_player(self, player_name: str):
        """
        Get the last message sent by a given player.
        """
        for message in reversed(self._messages):
            if message.agent_name == "System" and player_name in message.visible_to:
                return message
        return None

    def get_all_messages(self) -> List[Message]:
        """
        Get all the messages in the pool.

        Returns:
            List[Message]: A list of all messages.
        """
        return self._messages

    def get_visible_messages(self, agent_name, turn: int, history: bool = True) -> List[Message]:
        """
        Get all the messages that are visible to a given agent before a specified turn.

        Parameters:
            agent_name (str): The name of the agent.
            turn (int): The specified turn.

        Returns:
            List[Message]: A list of visible messages.
        """

        # Get the messages before the current turn
        if history:
            prev_messages = [message for message in self._messages if message.turn <= turn]
        else:
            prev_messages = [message for message in self._messages if message.turn == turn]

        visible_messages = []
        for message in prev_messages:
            if message.visible_to == "all" or agent_name in message.visible_to:
                visible_messages.append(message)
        return visible_messages
