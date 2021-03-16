import random
import time
import discord
from discord.ext import commands
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import urllib
from urllib.request import Request

try:
    from PIL import Image, ImageFile, ImageOps, ImageDraw, ImageFont
except Exception as error:          # this is to avoid heroku being dum dum with pillow dependency
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
            user_row.last_modified = current  # update time for xp
            print(f'{author} has now {user_row.xp} xp')
            lvl = user_row.level
            lvl_calc = 5 * (lvl ** 2) + (50 * lvl) + 100 - user_row.xp_lvl  # how much xp needed for the next level
            print(lvl_calc)
            if lvl_calc <= 0:
                user_row.level += 1
                user_row.xp_lvl = 0 + abs(
                    lvl_calc)  # level up, reset the xp counter and add what remained from the last level
                print(f'User {author} has leveled up to level {user_row.level}.')
                embed = discord.Embed(title='',
                                      description=f'{author.mention} has leveled up to level **{user_row.level}**, chuckle.',
                                      color=0xff005a)
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
    exc = 'none'
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
            except Exception as exc:
                err = True
                stats[ids.id_user] = f'Total XP: {ids.xp} | Level: {ids.level} | Position: {pos}\n'
            pos += 1
    if err:
        print('There was an error making the lb, probably a user in the page isn\'t in the server')
    return stats


async def change_bg(user_id, url):
    if url == 'none':
        url = 'https://cdn.discordapp.com/attachments/819169940400635908/820605358930001930/bg_empty.png'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
        bg = Image.open(urllib.request.urlopen(req)).convert('RGBA').crop((0, 0, 934, 282))
    except Exception as error1:
        return str(error1)
    url_db = db.session.query(LevelDatabase).filter_by(id_user=str(user_id)).first()
    url_db.bg_link = url
    db.session.commit()
    return '1'


def add(id_user, xp, level):  # XP TOTALI - XP LIVELLI PREC
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

    @commands.command(aliases=['bg'])
    async def background(self, ctx, url='none'):
        value = await change_bg(ctx.author.id, url)
        if value != '1':
            await ctx.reply(
                f"**Fool.**\nCouldn't get an image from the link, try with a different link.\n```{value}```",
                mention_author=False)
        else:
            await ctx.reply(
                'Changed background image <:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa:737675219937787974>\n(Use .bg to set default bg)',
                mention_author=False)

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
        message = '```\n'
        page -= 1
        with ctx.typing():
            stats = await get_all(ctx, start=page * 20, end=(page * 20) + 20)
            for i in stats.keys():
                message += f'{i}: {stats[i]}'
            message += '```'
        if message == '```\n```':
            return await ctx.reply(f'There is no such thing as page {page + 1}.', mention_author=False)
        return await ctx.reply(message, mention_author=False)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await add_xp(message.author, message.channel)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            await add_new_user(member.id)

    @commands.command()
    async def rank(self, ctx, user='none'):

        if user == 'none':
            user = str(ctx.author.id)

        if len(ctx.message.mentions) == 0:
            if not user.isnumeric():
                return await ctx.reply('Specify a user, or the user will specify you.', mention_author=False)
            if len(user) != 18:
                return await ctx.reply('Specify a user, or the user will specify you.', mention_author=False)

        else:
            user = ctx.message.mentions[0].id
        level = await check_level(user)

        try:
            if level[0] >= 0:

                member = await ctx.guild.fetch_member(user)

                # mask for circle crop
                await member.avatar_url.save("pics/avatar.png")
                mask = Image.new('L', (200, 200), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0) + (200, 200), fill=255)

                # import bg from link and avatar
                overlay = Image.open("pics/light.png").convert('RGBA')
                img = Image.open("pics/avatar.png").convert('RGBA').resize((200, 200), resample=0)
                try:
                    req = urllib.request.Request(level[4],
                                                 headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'})
                    bg = Image.open(urllib.request.urlopen(req)).convert('RGBA').resize((934, 282)).crop(
                        (0, 0, 934, 282))  # TODO: Crop? Resize?
                except Exception as err:
                    await ctx.reply(
                        f'There was an error while retrieving/processing the background image, using default image\n```{err}\nWelcome to the Cloud Room.```',
                        mention_author=False)
                    bg = Image.open('pics/bg_empty.png').convert('RGBA')

                # fit overlay on bg
                bg.paste(overlay, (0, 0), overlay)
                ImageOps.expand(bg, border=300, fill=(37, 150, 190, 0)).save('pics/expand.png')

                # fit mask on avatar
                avatar = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
                avatar.putalpha(mask)

                # paste avatar on bg
                bg.paste(avatar, (36, 48), avatar)
                bg.save('pics/bg.png', "png")

                # add text to it
                bg = Image.open("pics/bg.png")
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

    @commands.command()
    async def embedtest(self, ctx):
        embed = discord.Embed(title='epic embed fail', description='', color=0xff005a)
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Level(client))


if __name__ == '__main__':
    app.run()
