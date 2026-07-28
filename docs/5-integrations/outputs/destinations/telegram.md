# Telegram

Output detections and audit (only) to a Telegram chat, group, or channel.

- `bot_token`: the Telegram Bot API token obtained from @BotFather.
- `chat_id`: the ID of the target chat, group, or channel that receives the messages.
- `parse_mode`: (optional) message formatting mode: `Markdown`, `MarkdownV2`, or `HTML`.
- `message`: (optional) a template string for custom message formatting.

Example:

```text
bot_token: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
chat_id: -1001234567890
parse_mode: Markdown
```

## Provisioning

To use this Output, create a Telegram Bot:

1. Open Telegram. Send a message to [@BotFather](https://t.me/BotFather)
2. Send `/newbot`. Obey the prompts to name your bot
3. Copy the bot token. This is the `bot_token` that you need in LimaCharlie
4. Add the bot to the chat, group, or channel that receives the messages
5. For channels, add the bot as an administrator with "Post Messages" permission
6. Get the `chat_id` for your target:
    - For **private chats**: send a message to the bot, then open `https://api.telegram.org/bot<TOKEN>/getUpdates` to find your chat ID
    - For **groups**: add the bot to the group, send a message, then check `getUpdates` for the group's chat ID (a negative number)
    - For **public channels**: use `@channelusername` as the chat ID
