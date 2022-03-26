import sys

from discord.app_commands import command, guilds, check
from discord import Interaction, TextStyle, Embed
from traceback import print_stack, format_exc
from discord.ext.commands import Cog, Bot
from discord.ui import Modal, TextInput
from asyncio import get_event_loop
from paginator import Paginator
from mystbin import Client
from io import StringIO

from utils import test_server, is_owner, default_color


mystbin_client = Client()


async def evaluate_code(interaction: Interaction, code: str) -> str:
	old_stdout = sys.stdout
	redirected_output = sys.stdout = StringIO()

	try: exec(code)
	except Exception as e:
		print_stack(file=sys.stdout)
		print(sys.exc_info())

	stdout = old_stdout

	return str(redirected_output.getvalue())

def format_output(_input: str, output: str) -> str:
	return f"Input:\n```py\n{_input}\n```\nOutput:\n```cmd\n{output}\n```"


class Eval_modal(Modal, title="Eval"):
	code = TextInput(label="Code", style=TextStyle.paragraph, default="print()", required=True)

	async def on_submit(self, interaction: Interaction):
		if self.code == "print()":
			await interaction.response.send_message('True', ephemeral=True)
			return

		output = await evaluate_code(interaction, self.code)

		kwargs = {
			'ephemeral': True
		}

		if len(output) < 2000:
			await interaction.response.send_message(embed=Embed(description=output, color=default_color))
			return

		pages = []
		for i in range(0, len(output), 2000 - len(self.code)):
			new_output = ""
			new_output = Embed(description=format_output(self.code, output[i:i+2000-len(code)]), color=default_color)
			
			pages.append(new_output)

		if (new_output): pages.append(new_output)

		await Paginator(interaction, pages).start(True)


class Dev(Cog):
	def __init__(self, bot):
		self.bot = bot


	@command()
	@guilds(test_server)
	@check(is_owner)
	async def eval(self, interaction: Interaction, code: str = None, formatted: bool = True, ephemeral: bool = False, mystbin: bool = False, timeout: float = 300.0):
		bot = self.bot

		if (code):
			output = await evaluate_code(interaction, code)

			kwargs = {
				"ephemeral": ephemeral
			}

			if (mystbin):
				kwargs['content'] = await mystbin_client.post("# Input\n" + code + "\n\n\n\n# Output\n" + output, syntax="python")
			else:
				if len(output) > 2000:
					pages = []
					for i in range(0, len(output), 2000 - len(code)):
						if not (formatted): new_output = output[i:i+2000-len(code)]
						else: new_output = Embed(description=format_output(code, output[i:i+2000-len(code)]), color=default_color)

						pages.append(new_output)

					if (new_output): pages.append(new_output)

					await Paginator(interaction, pages).start(formatted)
					return

				else:
					if not (formatted): kwargs['content'] = output 
					else: kwargs['embed'] = Embed(description=format_output(code, output), color=default_color)

			await interaction.response.send_message(**kwargs)
			return

		modal = Eval_modal(timeout=timeout)
		await interaction.response.send_modal(modal)
		await modal.wait()


async def setup(bot):
	await bot.add_cog(Dev(bot))