import random
import time
import discord
from discord.ext import commands
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import aiohttp
from io import BytesIO
import markovify

try:
    from PIL import Image, ImageFile, ImageOps, ImageDraw, ImageFont
except Exception as error:  # this is to avoid heroku being dum dum with pillow dependency
    print(error)
    import Image
    import ImageFile
    import ImageOps
    import ImageDraw
    import ImageFont

with open('priv.txt', 'r') as e:
    privdb = e.read()

with open('pub.txt', 'r') as f:
    pubdb = f.read()

ImageFile.LOAD_TRUNCATED_IMAGES = True

app = Flask(__name__)

ENV = 'prod'

if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = privdb
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = pubdb

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

priv_channels = (404841053242523668, 738075158467837962, 761039653951766569, 821798504405663815)


class LevelDatabase(db.Model):
    __tablename__ = 'levels'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Text)
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=0)
    last_modified = db.Column(db.Integer, default=1615398960)
    xp_lvl = db.Column(db.Integer, default=0)
    bg_link = db.Column(db.Text,
                        default='https://cdn.discordapp.com/attachments/819169940400635908/820605358930001930/bg_empty.png')

    def __init__(self, id_user, xp, level, last_modified, xp_lvl, bg_link):
        self.id_user = id_user
        self.xp = xp
        self.level = level
        self.last_modified = last_modified  # last time xp was added, unix epoch
        self.xp_lvl = xp_lvl  # xp since last level
        self.bg_link = bg_link


async def add_new_user(author):
    if db.session.query(LevelDatabase).filter(
            LevelDatabase.id_user == str(author)).count() == 0:  # if user doesn't appear in the db
        data = LevelDatabase(str(author), 0, 0, 1615398960, 0,
                             'https://cdn.discordapp.com/attachments/819169940400635908/820605358930001930/bg_empty.png')
        db.session.add(data)
        db.session.commit()
        return print(f'Added {author}.')
    else:
        print(f'{author} already added.')


async def add_xp(author, channel):
    if db.session.query(LevelDatabase).filter(
            LevelDatabase.id_user == str(author.id)).count() != 0:  # if user is in database

        user_row = db.session.query(LevelDatabase).filter_by(id_user=str(author.id)).first()
        current = int(time.time())  # current time
        if current - user_row.last_modified < 60:  # if current time is less than a minute ahead of last time xp was added, do nothing
            user_row.last_modified = current
            db.session.commit()
            return
        else:
            num = random.randint(15, 25)  # add random xp between 15 and 25
            user_row.xp_lvl += num
            user_row.xp += num
            user_row.last_modified = current  # update time for xp
            lvl = user_row.level
            lvl_calc = 5 * (lvl ** 2) + (50 * lvl) + 100 - user_row.xp_lvl  # how much xp needed for the next level
            if lvl_calc <= 0:
                user_row.level += 1
                user_row.xp_lvl = 0 + abs(
                    lvl_calc)  # level up, reset the xp counter and add what remained from the last level
                embed = discord.Embed(title='',
                                      description=f'{author.mention} has leveled up to level **{user_row.level}**, chuckle.',
                                      color=0xff005a)
                print(channel.id)
                if channel.id not in priv_channels:
                    await channel.send(embed=embed)
                else:
                    channel.id = 343323003288813569
                    await channel.send(embed=embed)
            db.session.commit()
            return
    else:
        await add_new_user(author.id)
        print(f'{author} not in DB, so I added him.')


async def check_level(author):
    if db.session.query(LevelDatabase).filter(LevelDatabase.id_user == str(author)).count() != 0:
        user_row = db.session.query(LevelDatabase).filter_by(id_user=str(author)).first()
        lvl_tot = 5 * (user_row.level ** 2) + (50 * user_row.level) + 100
        return user_row.level, user_row.xp, user_row.xp_lvl, lvl_tot, user_row.bg_link
    else:
        return -1


async def get_all(ctx, start, end):
    err = False
    stats = {}
    list_db = db.session.query(LevelDatabase).order_by(desc(LevelDatabase.xp))[start:end]
    pos = start + 1
    if ENV == 'dev':
        for ids in list_db:
            # print(await ctx.guild.fetch_member(ids.id_user)) # for final deploy
            stats[ids.id_user] = f'Total XP: {ids.xp} | Level: {ids.level} | Position: {pos}°\n'
            pos += 1
    else:
        for ids in list_db:
            # noinspection PyBroadException
            try:
                stats[await ctx.guild.fetch_member(
                    ids.id_user)] = f'Total XP: {ids.xp} | Level: {ids.level} | Position: {pos}\n'
            except Exception:
                err = True
                stats[ids.id_user] = f'Total XP: {ids.xp} | Level: {ids.level} | Position: {pos}\n'
            pos += 1
    if err:
        print('There was an error making the lb, probably a user in the page isn\'t in the server')
    return stats


async def change_bg(user_id, url):
    if url == 'none':
        url = 'https://cdn.discordapp.com/attachments/819169940400635908/820605358930001930/bg_empty.png'
        url_db = db.session.query(LevelDatabase).filter_by(id_user=str(user_id)).first()
        url_db.bg_link = url
        db.session.commit()
        return '1'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}) as r:
                pic = BytesIO(await r.read())
                Image.open(pic).convert('RGBA').crop((0, 0, 934, 282))
    except Exception as error1:
        return str(error1)
    url_db = db.session.query(LevelDatabase).filter_by(id_user=str(user_id)).first()
    url_db.bg_link = url
    db.session.commit()
    return '1'


def add(id_user, xp, level):  # XP TOT - XP PREV LEVELS
    if db.session.query(LevelDatabase).filter(
            LevelDatabase.id_user == str(id_user)).count() == 0:  # if user doesn't appear in the db

        i = level - 1
        xp_lvl = 0
        while i >= 0:
            xp_lvl += 5 * (i ** 2) + (50 * i) + 100
            i -= 1

        xp_lvl = xp - xp_lvl

        data = LevelDatabase(str(id_user), xp, level, 1615398960, xp_lvl,
                             'https://cdn.discordapp.com/attachments/819169940400635908/820605358930001930/bg_empty.png')

        db.session.add(data)
        db.session.commit()
        return print(f'Added {id_user}.')
    else:
        user_row = db.session.query(LevelDatabase).filter_by(id_user=str(id_user)).first()
        user_row.xp = xp
        user_row.level = level
        i = level - 1
        xp_lvl = 0
        while i >= 0:
            xp_lvl += 5 * (i ** 2) + (50 * i) + 100
            i -= 1

        xp_lvl = xp - xp_lvl
        user_row.xp_lvl = xp_lvl
        db.session.commit()
        print(f'{id_user} updated info')


def round_corner(radius, fill):
    """Draw a round corner"""
    corner = Image.new('RGB', (radius, radius), (32, 41, 47, 0))
    draw = ImageDraw.Draw(corner)
    draw.pieslice((0, 0, radius * 2, radius * 2), 180, 270, fill=fill)
    return corner


def round_rectangle(size, radius, fill):
    """Draw a rounded rectangle"""
    width, height = size
    rectangle = Image.new('RGB', size, fill)
    corner = round_corner(radius, fill)
    rectangle.paste(corner, (0, 0))
    rectangle.paste(corner.rotate(90), (0, height - radius))  # Rotate the corner and paste it
    rectangle.paste(corner.rotate(180), (width - radius, height - radius))
    rectangle.paste(corner.rotate(270), (width - radius, 0))
    return rectangle


add_users = (544556502573121554, 259280989715562496)


class Level(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await add_xp(message.author, message.channel)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            await add_new_user(member.id)

    @commands.command(aliases=['bg'])
    async def background(self, ctx, url='none'):
        with ctx.typing():
            value = await change_bg(ctx.author.id, url)
            if value != '1':
                return await ctx.reply(
                    f"**Fool.**\nCouldn't get an image from the link, please specify a valid link to an image to set as background for your rank card.\n```{value}```",
                    mention_author=False)
            else:
                return await ctx.reply(
                    'Changed background image <:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:737675219937787974>\n(Use .bg to set default bg)',
                    mention_author=False)

    @commands.command(aliases=['haelp', 'commands'])
    async def help(self, ctx):
        help_em = discord.Embed(
            title='command the onion',
            color=0xff005a
        )
        help_em.add_field(name='.rank (User ID/tag [optional])', value='Current rank shown in a convenient card™')
        help_em.add_field(name='.lb/.leaderboard/.levels (Page #, default is 1)', value='Leaderboard of powerful flesh ridden beings', inline=False)
        help_em.add_field(name='.background/.bg (image link)', value='Change the background of your .rank card, if link isn\'t specified it restores the default (has to be link to an image and not a file)', inline=False)
        help_em.add_field(name='.mk', value='Generate wacky and unpredictable sentences, Reginald will watch from the heavens :place_of_worship:')
        help_em.set_thumbnail(url='https://cdn.discordapp.com/attachments/819169940400635908/825316562633359390/d.png')
        help_em.set_footer(text='remember to onion your lawn')

        await ctx.reply(embed=help_em, mention_author=False)

    @commands.command()
    async def mk(self, ctx):
        chan = discord.Client.get_channel(self.client, id=294479294040768524)
        messages = await chan.history(limit=500).flatten()
        thing = ""
        forbidden = (".mk", ".rank", ".lb", "!rank", "!levels")
        for msg in messages:
            if not msg.author.bot:
                if msg.content not in forbidden:
                    thing += f"{msg.content}\n"
        markov = markovify.NewlineText(thing)
        try:
            await ctx.send(markov.make_sentence(tries=200))
        except discord.errors.HTTPException:
            print('sad')
            return

    @commands.command()
    async def add(self, ctx, id_user, xp, lvl):
        if ctx.author.id not in add_users:
            return await ctx.reply('You can\'t run this command!', mention_author=False)
        try:
            await ctx.guild.fetch_member(id_user)
        except discord.errors.NotFound:
            return await ctx.reply('User ID error, user not in guild?', mention_author=False)
        else:
            try:
                add(id_user, int(xp), int(lvl))
                return await ctx.reply(f'Added {id_user}!', mention_author=False)
            except Exception as add_err:
                return await ctx.reply(f'Add function error\n{add_err}', mention_author=False)

    @commands.command(aliases=['leaderboard', 'levels'])
    async def lb(self, ctx, page: int = 1):

        if not page >= 1:
            return await ctx.reply(f'There is no such thing as page {page}.', mention_author=False)

        with ctx.typing():

            err = False
            added = False
            page -= 1
            list_db = db.session.query(LevelDatabase).order_by(desc(LevelDatabase.xp))[page * 21:(page * 21) + 21]
            pos = (page * 21) + 1

            lb_emb = discord.Embed(
                title="r/surrealmemes Server Leaderboard",
                description=f"Page {page + 1} | Positions: {(page * 21) + 1} to {(page * 21) + 21}",
                color=0xff005a
            )

            for ids in list_db:
                try:
                    lb_emb.add_field(name=f'{pos} | {str(await ctx.guild.fetch_member(ids.id_user))[:-5]}',
                                     value=f"Total XP: {ids.xp} | Level: {ids.level}")
                    added = True
                except discord.errors.NotFound:
                    lb_emb.add_field(name=f'{pos} | {ids.id_user}', value=f"Total XP: {ids.xp} | Level: {ids.level}")
                    added = True
                    err = True
                pos += 1
            if not added:
                return await ctx.reply(f'There is no such thing as page {page + 1}.', mention_author=False)
            if err:
                print('There was an error making the lb, probably a user in the page isn\'t in the server')
        return await ctx.reply(embed=lb_emb, mention_author=False)

    @commands.command()
    async def rank(self, ctx, user='none'):

        if user == 'none':
            user = str(ctx.author.id)

        if len(ctx.message.mentions) == 0:
            if not user.isnumeric():
                return await ctx.reply('Specify a user, or the user will specify you.', mention_author=False)
            try:
                await ctx.guild.fetch_member(user)
            except discord.errors.NotFound:
                return await ctx.reply('Specify a user, or the user will specify you\n(Invalid User ID).',
                                       mention_author=False)
        else:
            user = ctx.message.mentions[0].id
        level = await check_level(user)

        try:
            if level[0] >= 0:

                with ctx.typing():

                    member = await ctx.guild.fetch_member(user)

                    # mask for circle crop
                    await member.avatar_url.save("pics/avatar.png")
                    mask = Image.new('L', (200, 200), 0)
                    draw = ImageDraw.Draw(mask)
                    draw.ellipse((0, 0) + (200, 200), fill=255)

                    # import bg from link and avatar
                    overlay = Image.open("pics/overlay.png").convert('RGBA')
                    img = Image.open("pics/avatar.png").convert('RGBA').resize((200, 200), resample=0)
                    try:
                        async with aiohttp.ClientSession() as session1:
                            async with session1.get(level[4], headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}) as r:
                                pic = BytesIO(await r.read())
                                bg = Image.open(pic).convert('RGBA').resize((934, 282))
                    except Exception as err:
                        await ctx.reply(
                            f'There was an error while retrieving/processing the background image, using default image\n```{err}\nWelcome to the Cloud Room.```',
                            mention_author=False)
                        bg = Image.open('pics/bg_empty.png').convert('RGBA')

                    # fit overlay on bg
                    bg.paste(overlay, (0, 0), overlay)

                    # fit mask on avatar
                    avatar = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
                    avatar.putalpha(mask)

                    # paste avatar on bg
                    bg.paste(avatar, (36, 43), avatar)

                    # add text to it
                    bg1 = ImageDraw.Draw(bg)
                    font = ImageFont.truetype('pics/sansb.ttf', 45)
                    bg1.text((310, 132), f'Level: {level[0]} | Total XP: {level[1]}', font=font,
                             fill=(40, 40, 40))  # text shadow
                    bg1.text((312, 130), f'Level: {level[0]} | Total XP: {level[1]}', font=font,
                             fill=(0, 0, 0))  # actual text

                    # level meter
                    perc = round(level[2] / level[3], 2)
                    thing = round_rectangle((int(563 * perc), 20), 10, (37, 150, 190, 0))
                    bg.paste(thing, (325, 187))

                    bg.save("pics/big.png")

                    file = discord.File('pics/big.png')

                await ctx.reply(file=file, mention_author=False)
            else:
                await ctx.reply('There was an error! The sky has now turned a funky color.', mention_author=False)
        except Exception as err:
            print(err)
            return await ctx.reply(
                'There was an error! (Maybe user isn\'t in the server?) The sky has now turned a funky color.',
                mention_author=False)


def setup(client):
    client.add_cog(Level(client))


if __name__ == '__main__':
    app.run()
