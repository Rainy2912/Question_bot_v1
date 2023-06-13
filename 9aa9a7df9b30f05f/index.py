import discord, asyncio
from os import system
from discord_components import DiscordComponents, ComponentsBot, Button, Select, SelectOption, ButtonStyle
import json
import sqlite3
from datetime import datetime
import os

intents = discord.Intents.all()
client = discord.Client(intents=intents)

def sql_join():
    try:
        sql = sqlite3.connect("base.db")
        woogi = sql.cursor()
        return sql, woogi
    except:
        return False, False

def check_q_channel(user_id, admin):
    sql, woogi = sql_join()
    if sql:
        woogi.execute(f"SELECT * FROM check_q_channel WHERE user_id = {user_id} AND admin = '{admin}'")
        sql.commit()
        result = woogi.fetchone()
        sql.close()
        if result is None:
            return False
        else:
            return True
    else:
        return True

def create_channel_db(channel_id, user_id, admin):
    sql, woogi = sql_join()
    if sql:
        woogi.execute(f"INSERT INTO check_q_channel (channel_id, user_id, admin) values ({channel_id}, {user_id}, '{admin}')")
        sql.commit()
        sql.close()

def delete_channel_db(channel_id, admin):
    sql, woogi = sql_join()
    if sql:
        woogi.execute(f"DELETE FROM check_q_channel WHERE channel_id = {channel_id} AND admin = '{admin}'")
        sql.commit()
        sql.close()

def get_channel_id(user_id):
    sql, woogi = sql_join()
    if sql:
        woogi.execute(f"SELECT * FROM check_q_channel WHERE user_id = {user_id}")
        sql.commit()
        result = woogi.fetchone()
        sql.close()
        if result is None:
            return 0
        return result[0]

def check_channel(channel_id):
    sql, woogi = sql_join()
    if sql:
        woogi.execute(f"SELECT * FROM check_q_channel WHERE channel_id = {channel_id}")
        sql.commit()
        result = woogi.fetchone()
        sql.close()
        if result is None:
            return False
        else:
            return True
    else:
        return False

def check_user(channel_id):
    sql, woogi = sql_join()
    if sql:
        woogi.execute(f"SELECT * FROM check_q_channel WHERE channel_id = {channel_id}")
        sql.commit()
        result = woogi.fetchone()
        sql.close()
        if result is None:
            return False
        else:
            return result[1]
    else:
        return False

@client.event
async def on_ready():
    print("READY")
    DiscordComponents(client)

@client.event
async def on_message(message):
    if message.author.bot:
        return None
    guild = client.get_guild("길드값을 숫자로만 넣어주세요") #수정이 필요합니다
    log_channel = client.get_channel("채널 값을 숫자로만 넣어주세요") #수정이 필요합니다
    admin_role = discord.utils.get(guild.roles, name="우기") #수정이 필요합니다 관리자 디스코드 역할 이름을 적어주세요

    if admin_role in message.author.roles:
        if message.content.startswith("#셋팅"):
            with open("config.json", 'r', encoding='utf-8 sig') as file:
                data = json.load(file)
                components = []
                for i in data["config"]:
                    if data['config'][i]['color'] == "green":
                        style = ButtonStyle.green
                    elif data['config'][i]['color'] == "blue":
                        style = ButtonStyle.blue
                    elif data['config'][i]['color'] == "red":
                        style = ButtonStyle.red
                    else:
                        style = ButtonStyle.gray
                    components.append(Button(label=data["config"][i]["btn_name"], custom_id=data["config"][i]["btn_id"], style=style))
            await message.channel.send(
                embed=discord.Embed(description=f"> 원하는 관리자의 닉네임이 적혀있는 버튼을 눌러주세요\n\n> 신중히 미리 생각 후 문의를 진행해주세요\n\n> 장난 문의일경우 제재가 이루어질 수 있습니다"),
                components = [ 
                    components
                ]
            )
    elif message.content.startswith("#카테고리"):
        print(message.channel.category.id)
    elif message.content.startswith("#길드"):
        print(message.guild.id)
    elif message.content.startswith("#문의종료"):
        admin = message.channel.category.name
        file = discord.File(f"log/{message.channel.id}.txt")
        now = datetime.now()
        new_author = client.get_user(int(check_user(message.channel.id)))
        embed = discord.Embed(title='{}'.format(now.strftime("%Y - %m - %d")), color=0x50bcdf, timestamp=message.created_at)
        embed.add_field(name="문의 종료 로그", value=f"문의한 유저 : <@{new_author.id}>\n\n문의 종료 담당자 : <@{message.author.id}>", inline=True)
        embed.set_footer(text='SYSTEM', icon_url=client.user.avatar_url)
        await log_channel.send(embed=embed)
        log = await log_channel.send(file=file)
        os.remove(f"log/{message.channel.id}.txt")
        delete_channel_db(message.channel.id, admin)
        await message.channel.delete()
        await new_author.send(embed=discord.Embed(description=f"안녕하세요 {new_author.name}님\n\n> 현재 {admin}님과의 문의가 종료되었으며 다시 문의하고싶으신경우 다시 버튼을 클릭하여 문의해주세요"))
    else:
        if check_channel(message.channel.id) == True:
            if message.attachments:
                open(f"log/{message.channel.id}.txt", 'a', encoding='utf-8 sig').write(f"{message.author.name}({message.author} | {message.author.id}) : {message.content}, {message.attachments[0].url}\n")
            else:
                open(f"log/{message.channel.id}.txt", 'a', encoding='utf-8 sig').write(f"{message.author.name}({message.author} | {message.author.id}) : {message.content}\n")

@client.event
async def on_button_click(interaction):
    if interaction.responded:
        return
    id = interaction.custom_id
    with open("config.json", 'r', encoding='utf-8 sig') as file:
        data = json.load(file)
        if data['config'][id]:
            if check_q_channel(interaction.author.id, id) == True:
                await interaction.send(embed=discord.Embed(description=f"이미 해당 관리자와의 문의채널이 활성화 되어있습니다\n\n> 채널 : <#{get_channel_id(interaction.author.id)}>"))
            else:
                channel = await interaction.guild.create_text_channel(interaction.author.name, category=client.get_channel(int(data['config'][id]['category'])), overwrites={interaction.author: discord.PermissionOverwrite(read_messages=True, send_messages=True)})
                create_channel_db(channel.id, interaction.author.id, id)
                await interaction.send(embed=discord.Embed(description=f"해당 관리자에게 문의가 가능한 채널이 생성되었습니다\n\n> 문의 채널 : <#{channel.id}>"))
                now = datetime.now()
                open(f"log/{channel.id}.txt", 'a', encoding='utf-8 sig').write(f"{now.strftime('%Y - %m - %d')} 문의 채널 생성됨")
                embed = discord.Embed(title='{}'.format(now.strftime("%Y - %m - %d")), description=f"{interaction.author.name}님이 문의를 시작했어요!", color=0x50bcdf)
                embed.set_footer(text='SYSTEM', icon_url=client.user.avatar_url)
                await channel.send(content="@everyone", embed=embed)
                

client.run("")
