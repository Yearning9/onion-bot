import random
import discord
from discord.ext import commands

with open('token.txt', 'r') as j:
    privdata = j.read()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)
TOKEN = privdata


bot.remove_command("help")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game('with the garlic'))
    print(
        f'h'
    )
    
    
@bot.command()
async def sad(ctx, *, message):
    sad1 = message.replace('o', '<:sad:562509148239953940>')
    sad2 = sad1.replace('O', '<:sad:562509148239953940>')
    try:
        await ctx.send(sad2)
    except discord.errors.HTTPException:
        await ctx.send('Message was t<:sad:562509148239953940><:sad:562509148239953940> l<:sad:562509148239953940>ng to send <:sad:562509148239953940>')


@bot.event
async def on_member_join(member):
    channel = bot.get_channel(294481211030765568)
    ment = member.mention
    discrim = member.discriminator
    name = member.name
    variable = [
        f"Cover yourself in oil.",
        f"There are no faces.",
        f"You do not recognize the bodies in the water.",
        f"Your vertices will now be confiscated.",
        f"Here is your complementary 55 gallon drum of E.",
        f"The One in Pain is not to be disobeyed.",
        f"The Great Cosmic Prism sees all.",
        f"The number 7 is not real in Universe #7777777.",
        f"Praise Tim the Great and Powerful.",
        f"Show us your `[Error: Undefined]` certificate.",
        f"Please fill out your Life Permission Form before continuing.",
        f"The Noided One will screech at you while you sleep.",
        f"The Dave is cool and good.",
        f"Do not forget to widen your lemg.",
        f"The Hive Assimilator will now convert you into bees.",
        f"Undulate with style and grace.",
        f"You are now cake.",
        f"Garlic is the only ingredient you need.",
        f"The Void will consume you someday.",
        f"It has been well documented that the sky is actually paper and crayon.",
        f"Don't forget to head on down to your local VoidMart and peruse their wide selection of items.",
        f"Please know that you are loved.",
        f"Reginald is god.",
        f"Sooch is not for eating.",
        f"Limescale, rust, ground-in dirt.",
        f"W I G G L E .",
        f"actual content of the church in the fool. the worms that is a book of the bath soaps and",
        f"Lumien summoning ritual attempt beginning soon.",
        f"September 18th we all become empty husks.",
        f"Prepare for eternal gregation.",
        f"This is definitely not hell.",
        f"Gwa gwa.",
        f"No way the rock.",
        f"h.",
        f"2008 is inevitable.",
        f"We have been trying to reach you about your car's extended warranty.",
        f"BEES BEES BEES BEES BEES BEES BEES BEES.",
        f"This communication channel may or may not contain whalenuts.",
        f"This server consists of approximately 50% cool-and-goodness, 33% despair, 12% `[ERROR: FORBIDDEN]`, 3% Bees, 2% Garlic, and an old sock.",
        f"Your silverware has been relocated to Frog Balls, Arkansas.",
        f"Here is your complementary jar of soil.",
        f"The Azure Cold draws ever closer.",
        f"Garlic bread is love, garlic bread is life.",
        f"Care for a slice from the meat cylinder?",
        f"The worms shall eat into your brain... That is just a step.",
        f"This unit is not responsible for any loss of appetite, memory, hope, `[UNDEFINED]`, or Sedgewickness that may occur during your stay.",
        f"Boobis blomp. What even is that anymore...",
        f"Why settle for 3 dimensions when you can have all of them?",
        f"You seem to be warm currently. Don't worry, that can be fixed.",
        f"The Harvesters wish to speak to you about donating your organs.",
        f"Please enter your soul to continue...",
        f"Cron Cube is better than Corn Cube.",
        f"The current year is 2007.",
        f"Invest in GarlicCoin today!",
        f"Come rest your weary elbows.",
        f"Be very careful; The Hand roams this dimension.",
        f"I have successfully predicted your arrival.",
        f"If you are in need of assistence, then please visit Brogle Garden Centre Inc. for all your gardening, landscaping, and home care needs.",
        f"Don't forget your towel.",
        f"If you require sustenance, then head to your local Potato's Chip for quality eatings.",
        f"Your lucky numbers are 666 and 2008.",
        f"Thank you for allowing us to feast on your mind.",
        f"Beware the Lemons.",
        f"Please deposit any vegetals you may have into the incinerator before continuing.",
        f"Norm, Norm, no form.",
        f"The Hand has chosen you.",
        f"actual content of the bath soaps and",
        f"fool in the fool. The worms that is a good insult",
        f"Fun Fact: There are 48 Regular Polyhedra.",
        f"It is my displeasure to inform you that you are no longer real.",
        f"Congratulations! Your prize is: A Sad Feeling.",
        f"Post-Awareness Stage 6 is without description.",
        f"Click this link for a free pigeon. ---> <https://youtu.be/9bFioQgjmck>",
        f"Come and bask in my wisdom.",
        f"I hear that Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch is quite nice this time of year.",
        f"The Trout awaits you.",
        f"This is not a cult.", ]
    embed = discord.Embed(title=f'Welcome to the Realm of Madness, {name}#{discrim}.', description=random.choice(variable), color=0xff005a)
    await channel.send(embed=embed)


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author == bot.user:
        return
    variable = [
        f"Cover yourself in oil.",
        f"There are no faces.",
        f"You do not recognize the bodies in the water.",
        f"Your vertices will now be confiscated.",
        f"Here is your complementary 55 gallon drum of E.",
        f"The One in Pain is not to be disobeyed.",
        f"The Great Cosmic Prism sees all.",
        f"The number 7 is not real in Universe #7777777.",
        f"Praise Tim the Great and Powerful.",
        f"Show us your `[Error: Undefined]` certificate.",
        f"Please fill out your Life Permission Form.",
        f"The Noided One will screech at you while you sleep.",
        f"The Dave is cool and good.",
        f"Do not forget to widen your lemg.",
        f"The Hive Assimilator will now convert you into bees.",
        f"Undulate with style and grace.",
        f"You are now cake.",
        f"Garlic is the only ingredient you need.",
        f"The Void will consume you someday.",
        f"It has been well documented that the sky is actually paper and crayon.",
        f"Don't forget to head on down to your local VoidMart and peruse their wide selection of items.",
        f"Please know that you are loved.",
        f"Reginald is god.",
        f"Sooch is not for eating.",
        f"Limescale, rust, ground-in dirt.",
        f"W I G G L E .",
        f"actual content of the church in the fool. the worms that is a book of the bath soaps and",
        f"Lumien summoning ritual attempt beginning soon.",
        f"September 18th we all become empty husks.",
        f"Prepare for eternal gregation.",
        f"Gwa gwa.",
        f"No way the rock.",
        f"h.",
        f"2008 is inevitable.",
        f"We have been trying to reach you about your car's extended warranty.",
        f"BEES BEES BEES BEES BEES BEES BEES BEES.",
        f"This communication channel may or may not contain whalenuts.",
        f"This server consists of approximately 50% cool-and-goodness, 33% despair, 12% `[ERROR: FORBIDDEN]`, 3% Bees, 2% Garlic, and an old sock.",
        f"Cron Cube is better than Corn Cube.",
        f"Your silverware has been relocated to Frog Balls, Arkansas.",
        f"Here is your complementary jar of soil.",
        f"The Azure Cold draws ever closer.",
        f"Garlic bread is love, garlic bread is life.",
        f"Care for a slice from the meat cylinder?",
        f"The worms shall eat into your brain... That is just a step.",
        f"This unit is not responsible for any loss of appetite, memory, hope, [Undefined], or Sedgewickness that may occur during your stay.",
        f"Boobis blomp. What even is that anymore...",
        f"Why settle for 3 dimensions when you can have all of them?",
        f"You seem to be warm currently. Don't worry, that can be fixed.",
        f"The Harvesters wish to speak to you about donating your organs.",
        f"Please enter your soul to continue...",
        f"The current year is 2007.",
        f"Invest in GarlicCoin today!",
        f"Come rest your weary elbows.",
        f"Be very careful; The Hand roams this dimension.",
        f"I have successfully predicted this ping.",
        f"If you are in need of assistence, then please visit Brogle Garden Centre Inc. for all your gardening, landscaping, and home care needs.",
        f"Don't forget your towel.",
        f"If you require sustenance, then head to your local Potato's Chip for quality eatings.",
        f"Your lucky numbers are 666 and 2008.",
        f"Thank you for allowing us to feast on your mind.",
        f"Beware the Lemons.",
        f"Please deposit any vegetals you may have into the incinerator before continuing.",
        f"Norm, Norm, no form.",
        f"The Hand has chosen you.",
        f"The Trout awaits you.",
        f"actual content of the bath soaps and",
        f"fool in the fool. The worms that is a good insult",
        f"Fun Fact: There are 48 Regular Polyhedra.",
        f"It is my displeasure to inform you that you are no longer real.",
        f"Congratulations! Your prize is: A Sad Feeling.",
        f"Post-Awareness Stage 6 is without description.",
        f"Click this link for a free pigeon. ---> <https://youtu.be/9bFioQgjmck>",
        f"Come and bask in my wisdom.",
        f"I hear that Llanfairpwllgwyngyllgogerychwyrndrobwllllantysiliogogogoch is quite nice this time of year.",
        f"This is not a cult.", ]
    if bot.user.mentioned_in(message):
        await message.channel.send("{}".format(random.choice(variable)))
    if message.content.lower() == 'onion':
        await message.channel.send("onion")

bot.load_extension(f'levels')
print('Loaded Levels cog')


bot.run(TOKEN)
