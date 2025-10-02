"""
Pydantic models for Telegram webhook payloads.

These schemas represent the data structures sent by Telegram to the webhook endpoint.
They are part of the Infrastructure layer as they are specific to Telegram's API format.
"""

from pydantic import BaseModel, Field


class TelegramUser(BaseModel):
    """Represents a Telegram user."""

    id: int = Field(..., description="Unique identifier for this user or bot")
    is_bot: bool = Field(..., description="True if this user is a bot")
    first_name: str = Field(..., description="User's or bot's first name")
    last_name: str | None = Field(None, description="User's or bot's last name")
    username: str | None = Field(None, description="User's or bot's username")
    language_code: str | None = Field(None, description="IETF language tag of the user's language")


class TelegramChat(BaseModel):
    """Represents a Telegram chat."""

    id: int = Field(..., description="Unique identifier for this chat")
    type: str = Field(
        ..., description="Type of chat: 'private', 'group', 'supergroup', or 'channel'"
    )
    first_name: str | None = Field(
        None, description="First name of the other party in a private chat"
    )
    last_name: str | None = Field(
        None, description="Last name of the other party in a private chat"
    )
    username: str | None = Field(
        None, description="Username for private chats, supergroups and channels"
    )
    title: str | None = Field(None, description="Title for supergroups, channels and group chats")


class TelegramMessageEntity(BaseModel):
    """Represents one special entity in a text message (e.g., hashtags, usernames, URLs, etc.)."""

    type: str = Field(..., description="Type of the entity (e.g., 'bot_command', 'mention', 'url')")
    offset: int = Field(..., description="Offset in UTF-16 code units to the start of the entity")
    length: int = Field(..., description="Length of the entity in UTF-16 code units")
    url: str | None = Field(
        None,
        description="For 'text_link' only, URL that will be opened after user taps on the text",
    )
    user: TelegramUser | None = Field(
        None, description="For 'text_mention' only, the mentioned user"
    )


class TelegramMessage(BaseModel):
    """Represents a message from Telegram."""

    message_id: int = Field(..., description="Unique message identifier inside this chat")
    from_: TelegramUser | None = Field(
        None, alias="from", description="Sender of the message; empty for messages sent to channels"
    )
    chat: TelegramChat = Field(..., description="Conversation the message belongs to")
    date: int = Field(..., description="Date the message was sent in Unix time")
    text: str | None = Field(
        None, description="For text messages, the actual UTF-8 text of the message"
    )
    entities: list[TelegramMessageEntity] | None = Field(
        None, description="Special entities like usernames, URLs, bot commands, etc."
    )

    # Additional common fields (add more as needed)
    reply_to_message: "TelegramMessage | None" = Field(
        None, description="For replies, the original message"
    )
    edit_date: int | None = Field(None, description="Date the message was last edited in Unix time")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True  # Allow using both 'from' and 'from_' field names


class TelegramWebhookUpdate(BaseModel):
    """
    Represents an incoming update from Telegram webhook.

    This is the root model that Telegram sends to the webhook endpoint.
    """

    update_id: int = Field(..., description="The update's unique identifier")
    message: TelegramMessage | None = Field(
        None, description="New incoming message of any kind - text, photo, sticker, etc."
    )

    # Additional update types (add as needed)
    edited_message: TelegramMessage | None = Field(
        None, description="New version of a message that is known to the bot and was edited"
    )
    channel_post: TelegramMessage | None = Field(
        None, description="New incoming channel post of any kind"
    )
    edited_channel_post: TelegramMessage | None = Field(
        None, description="New version of a channel post that is known to the bot and was edited"
    )

    # Add more update types as needed:
    # callback_query, inline_query, chosen_inline_result, etc.
