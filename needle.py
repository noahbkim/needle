import disnake

import configparser
from typing import Set


class Bot(disnake.Client):
    """Override event callbacks, provide slash commands."""

    watch_channel_ids: Set[int]
    notify_channel_id: int

    def configure(self, section: configparser.SectionProxy):
        """Set watch and notify."""

        self.watch_channel_ids = set(map(int, section["watch"].split()))
        self.notify_channel_id = int(section["notify"])

    async def on_thread_create(self, thread: disnake.Thread):
        """Notify main channel on thread creation."""

        if thread.parent_id in self.watch_channel_ids:
            await thread.fetch_members()

            message_content = None
            async for message in thread.history(limit=2):
                message_content = message.content
                break

            embed = disnake.Embed(
                title=thread.name,
                description=f"> {message_content}" or f"{thread.owner.display_name} created a new thread.",
                timestamp=thread.create_timestamp,
                url=thread.jump_url,
            )
            embed.set_author(name=thread.owner.display_name, icon_url=thread.owner.avatar.url)
            embed.set_footer(text=f"#{thread.parent.name}")

            channel = self.get_channel(self.notify_channel_id)
            await channel.send(embed=embed)


def main():
    """Configure and start the bot."""

    config = configparser.ConfigParser()
    config.read("needle.conf")

    intents = disnake.Intents(
        messages=True,
        message_content=True,
        reactions=True,
        guilds=True,
        members=True,
        # members=True,
        # presences=True,
    )

    client_id = config["discord"]["client_id"]
    permissions = config["discord"]["permissions"]
    print(
        "https://discord.com/api/oauth2/authorize"
        f"?client_id={client_id}"
        f"&permissions={permissions}"
        "&scope=bot"
    )

    token = config["discord"]["token"]
    bot = Bot(intents=intents)
    bot.configure(config["needle"])
    bot.run(token)


if __name__ == "__main__":
    main()
