from base64 import encode
from encodings import utf_8
from typing_extensions import Self
import discord
from discord.ext import commands
import os
from os import system
from dotenv import load_dotenv
from numpy import source
import youtube_dl
from discord.utils import get
from discord import FFmpegPCMAudio
import asyncio
import urllib.request
import requests as re
from bs4 import BeautifulSoup
from apiclient.discovery import build




load_dotenv()
Mytoken = os.getenv('TOKEN')
MyAPI=os.getenv('API_KEY')
song_queue=[]
queue_list=[]
is_loop=False
intents = discord.Intents().all()
intents.members=True
bot=commands.Bot(command_prefix='.', intents=intents)
FFMPEG_OPTIONS ={"options":"-vn"}
YDL_OPTIONS={'format':"bestaudio",
'default_search': 'auto'}


#with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
   # url="GoodBoy"
    #info = ydl.extract_info(url,download=False)
    #print(info['entries'][0]["formats"][0]['url'])
    #url2=info['formats'][0]['url']
    #name=info['title']






async def music(ctx,url:str):
    if ctx.author.voice is None:
        await ctx.send("You are not in voice channel")
    channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    else:
        await ctx.voice_client.move_to(channel)
        
    voice=ctx.voice_client
    song_queue.append(url)
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url,download=False)
        if not voice.is_playing():

            if 'entries' in info:
                url2=info['entries'][0]['formats'][0]['url'] 
                name=info['entries'][0]['title']
                print(name)
            else:
                url2=info['formats'][0]['url']
                name=info['title']    
                
            queue_list.append(name)
            await ctx.send("Now playing : "+name)
            source = await discord.FFmpegOpusAudio.from_probe(url2,**FFMPEG_OPTIONS)
            voice.play(source,after=lambda e:play_next(ctx))
        else:
            if 'entries' in info:
                name=info['entries'][0]['title']
            else:
                name=info['title']    
            await ctx.reply(" Already add "+name+" to queue!")
            queue_list.append(name)

def play_next(ctx):
    voice=ctx.voice_client
    if len(song_queue)>0:
        if is_loop == False:
            del song_queue[0]
            del queue_list[0]
    
        if len(song_queue)>0:
            with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                url=song_queue[0]
                info = ydl.extract_info(url,download=False)

                if 'entries' in info:
                    url2=info['entries'][0]['formats'][0]['url'] 
                    
                else:
                    url2=info['formats'][0]['url']   

                source=discord.FFmpegPCMAudio(url2,**FFMPEG_OPTIONS)
                voice.play(source,after=lambda e:play_next(ctx))
                voice.volume = 30
        else:
            voice.disconnect(ctx)


@bot.command()
async def disconnect(ctx):
    await ctx.voice_client.disconnect()


@bot.command()
async def skip(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.pause()
    play_next(ctx)

@bot.command()
async def clear(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    song_queue.clear()
    queue_list.clear()
    voice.stop()
    

@bot.command()
async def queue(ctx):
    if len(queue_list)>1:
        await ctx.send("Now playing "+str(queue_list[0])+" \n ")
        await ctx.send('Song queued  : \n')
        for queue in queue_list[1:]:
            await ctx.send("Next queue "+str(queue)+" \n ")
    else:
        await ctx.send("No queue!")


@bot.command()
async def pause(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.pause()


@bot.command()
async def resume(ctx):
    voice = get(bot.voice_clients, guild=ctx.guild)
    voice.resume()



@bot.command()
async def loop(ctx):
    global is_loop
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice.is_playing():
        if is_loop==False:
            is_loop=True 
            await ctx.send("Loop on!")
        else:
            is_loop=False
            await ctx.send("Loop off!")
    else:
        await ctx.send("No song playing now!")

@bot.command()
async def play(ctx, *,url):
    await music(ctx,url)


@bot.command()
async def p(ctx, *,url):
    await music(ctx,url)

datacampdict={"art":"architect-finearts","health":"medical-health","science":"science","computer":"computer-it",
"law":"law","contest":"type/contest"}

def get_camp(type):
    camptype=datacampdict[type]
    itcamp=re.get("https://www.camphub.in.th/"+camptype)
    it_soup = BeautifulSoup(itcamp.text, 'html.parser')
    eni_data=[]
    for a in (it_soup.find_all('a', title=True)):
        eni_data.append(a['title'])
        eni_data=list(dict.fromkeys(eni_data))
    return eni_data

def get_url(type):
    camptype=datacampdict[type]
    itcamp=re.get("https://www.camphub.in.th/"+camptype)
    it_soup = BeautifulSoup(itcamp.text, 'html.parser')
    url_data=[]
    for a in (it_soup.find_all('a', title=True)):
        url_data.append(a['href'])
        url_data=list(dict.fromkeys(url_data))
    return url_data

    
@bot.command()
async def camp(ctx,ctype):
    eni_data=[]
    url_data=[]
    eni_data=get_camp(ctype)
    url_data=get_url(ctype)
    await ctx.send("ค่าย"+ctype)
    for i in range(len(eni_data)):
        await ctx.send(str(i+1)+". "+str(eni_data[i]+"\n"+url_data[i]))


@bot.command()
async def camptype(ctx):
    for i in range (len(datacampdict)):
        await ctx.send(list(datacampdict.keys())[i])


@bot.event
async def on_member_join(member):
    guild = bot.get_guild(member.guild.id)
    channel=bot.get_channel(member.guild.text_channels[1])
    print(member.guild.text_channels[0])
    
    await channel.send(f"{member.mention} has joined")
    await channel.send(f"Welcome to the {guild.name} server")
    await member.send(f"Welcome to the {guild.name} server")

@bot.event
async def on_member_remove(member):
    await bot.get_channel(member.guild.text_channels[1]).send(f"{member.mention} has left")

@bot.event
async def on_ready():
    print("READY!")

@bot.event
async def on_disconnect():
    voice = bot.voice_clients.guild
    song_queue.clear()
    queue_list.clear()
    voice.stop()


bot.run(Mytoken)