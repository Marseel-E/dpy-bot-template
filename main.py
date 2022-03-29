from discord import Intents, Status, Game
from discord.ext.commands import Bot
from os import environ, listdir
from dotenv import load_dotenv

from utils import test_server

load_dotenv('.env')


class BotTemplate(Bot):
	def __init__(self):
		super().__init__(command_prefix="\000002800", intents=Intents.default(), help_command=None, application_id=environ.get('APP_ID'))


	async def on_ready(self):
		print("running...")
		await self.change_presence(status=Status.online, activity=Game("bot-template.exe"))


	async def on_message(self, message): pass


	async def setup_hook(self):
		for cog in listdir('cogs'):
			if cog.endswith('.py'):
				try: await self.load_extension("cogs." + cog[:-3])
				except Exception as e: print(f"ERROR: couldn't load '{cog}'", "\n", e, "\n")
				else: print(f"INFO: loaded '{cog}'")

		await self.tree.sync()
		await self.tree.sync(guild=test_server)


if __name__ == '__main__':
	bot = BotTemplate()
	bot.run(environ.get('TOKEN'))
