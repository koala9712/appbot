import json
import re
import discord
import asyncio
import os
import sys
from discord.audit_logs import _transform_verification_level
from discord.errors import Forbidden, HTTPException, NotFound
from collections import Counter
from discord.ext import commands
from discord.ext.commands.core import check
import config
def get_prefix():
    with open(r"config/prefix.txt") as file:
        return file.read()
bot = commands.Bot(command_prefix=get_prefix())
bot.remove_command('help')

@bot.event
async def on_ready():
    print("logged in")
    await bot.fetch_channel(843773991055654926).send("online")

##########################################################################
################################## Help ##################################
################################# command ################################
##########################################################################

@bot.group(invoke_without_command=True)
async def help(ctx):
    em = discord.Embed(title="Help Page", description=f"use {get_prefix()}help <command> for a more detailed help on the command.")
    em.add_field(
        name="Admin Commands", 
        description=("""
            1) set_log_channel or (slc)\n
            2) dump_questions\n
            3) add_question\n
            4) rem_question
            5) set_app_channel\n
            6) blacklist\n
            7) whitelist\n
            8) toggle\n
            9) add_req\n
            10) remove_req\n
            11) write_hier\n
            """))
    em.add_field(name="Public Commands", description="1) raise_er\n2) apply")

em = discord.Embed(title="Test Embed", description="Just ensuring i cant send messages and embeds here")

async def log(content):
    with open(r"config\log.txt", "a") as file:
        file.write(content)
    with open(r"config/logch.txt") as file:
        x = int(file.read())
    ch = bot.get_channel(x)
    if ch != None:
        ch.send(content)
        return
    else:
        ch = bot.fetch_channel(x)
        if ch != None:
            ch.send(content)
            return
    return False

def add_question(cat, ques):
    with open(f"questions\{cat}.txt", "a") as file:
        file.write(ques)
    log(f"Added Question:\n{ques}\nin category {cat}")

def remove_question(cat, ques):
    with open(f"questions\{cat}.txt", "a") as file:
        file_source = file.read()
        file.write(file_source.replace(f"{ques}", ""))
    log(f"Removed Question:\n{ques}\nfrom category {cat}")

def get_id_from_mention(mention):
    return int(''.join(x for x in mention if x.isdigit()))

def write_log_channel(chid):
    with open(r"config/logch.txt", "w") as f:
        f.write(chid)
    log(f"Set <#{chid}> as log channel")

def write_applog(chid):
    with open(r"config/applog.txt", "w") as f:
        f.write(chid)
    log(f"Set <#{chid}> to log applications")

def write_blacklist_user(app, usrid):
    with open(r"bl\usr_blacklists.txt", "a") as f:
        f.write(f"{app}_{usrid}")
    log(f"Blacklisted user {usrid} for app {app}")

def write_blacklist_role(app, rlid):
    with open(r"b\rl_blacklists.txt", "a") as f:
        f.write(f"{app}_{rlid}")
    log(f"Blacklisted role {rlid} for app {app}")

def write_whitelist_user(app, usrid):
    with open(r"bl\usr_blacklists.txt", "r+") as f:
        file_source = f.read()
        f.write(file_source.replace(f"{app}_{usrid}", ""))
    log(f"Whitelisted user {usrid} for app {app}")


def write_whitelist_role(app, rlid):
    with open(r"bl\rl_blacklists.txt", "r+") as f:
        file_source = f.read()
        f.write(file_source.replace(f"{app}_{rlid}", ""))
    log(f"Whitelisted role {rlid} for app {app}")

@bot.command(name="set_log_channel", aliases = ["slc"])
@commands.has_permissions(manage_messages=True)
async def set_log_channel(ctx, channel):
    channel = get_id_from_mention(channel)
    if len(str(channel)) == 18:
        try:
            aio = bot.get_channel(channel)
            try:
                await aio.send(embed=em)
                write_log_channel(channel)
                await ctx.send(f"I configured <#{channel}> to log applications!")
            except:
                await ctx.send("I can't send messages and/or embeds in the specified channel, Please Ensure I am allowed to post embeds and messages in that channel/")
        except:
            await ctx.reply("The bot can not reach the channel, check permissions.")
    else:
        await ctx.send(f"Channel argument has been improperly passed.")

@bot.command(name="dump_questions")
async def dump_questions(ctx, cat):
    try:
        with open(f"{cat}.txt") as file:
            await ctx.send(file.read())
    except FileExistsError:
        await ctx.send("No such category!")
    except Exception as e:
        await ctx.send(e)


@bot.command(name="raise_er")
async def raise_er(ctx, *, context=None):
    try:
        me = await bot.fetch_user(736147895039819797)
        await me.send(f"User {ctx.author.id} raised error in server {ctx.message.guild} with context: {context}\nAnd{ctx.message.jump_url}")
        await ctx.send("The author of the bot has been notified of the error raised.")
    except Exception as e:
        await me.send(f"{ctx.message.jump_url}\n{e}")

@bot.command(name="add_question", aliases = ["ad", "add"])
async def add_question(ctx, cat, *, ques):
    try:
        add_question(cat, ques)
        await ctx.send(f"Added question `{ques}` in category `{cat}`")
    except Exception as e:
        await ctx.send(e)
@bot.command(name="rem_question", aliases = ["rem", "remove"])
async def rem_question(ctx, cat, *, ques):
    try:
        remove_question(cat, ques)
        await ctx.send(f"Removed question `{ques}` in category `{cat}`")
    except Exception as e:
        await ctx.send(e)
@bot.command(name="set_app_channel", aliases=['sac'])
async def set_app_channel(ctx, chid):
    channel = get_id_from_mention(chid)
    if len(str(channel)) == 18:
        try:
            aio = bot.get_channel(channel)
            try:
                await aio.send(embed=em)
                write_applog(channel)
                await ctx.send(f"I configured <#{channel}> to take applications!")
            except:
                await ctx.send("I can't send messages and/or embeds in the specified channel, Please Ensure I am allowed to post embeds and messages in that channel.")
        except:
            await ctx.reply("The bot can not reach the channel, check permissions.")
    else:
        await ctx.send(f"Channel argument has been improperly passed.")


@bot.command(name="blacklist")
async def blacklist(ctx, app, id):
    try:
        bot.fetch_user(id)
        write_blacklist_user(app, id)
    except HTTPException:
        await ctx.send("Error, could you please re-run the command")
    except NotFound:
        write_blacklist_role(id)

@bot.command(name="whitelist")
async def blacklist(ctx, app, id):
    try:
        bot.fetch_user(id)
        write_whitelist_user(app, id)
    except HTTPException:
        await ctx.send("Error, could you please re-run the command")
    except NotFound:
        write_whitelist_role(id)

@bot.command(nam="toggle")
async def toggle(ctx, on_or_off, app):
    details = f"{app}"
    with open(r"config\active_apps.txt", "a+") as file:
        x = file.readlines()
        if on_or_off == "on":
            if details in str(x):
                return
            else:
                file.write(f"\n{details}")
        elif on_or_off == "off":
            if details not in str(x):
                return
            else:
                with open(r"config\active_apps", "r+") as file2:
                    file_source = file2.read()
                    file2.write(file_source.replace(f"{details}", ""))

guild = bot.get_guild(727276010600530011)

async def return_name_of_role(id):
    role = guild.get_role(id)
    return role.name

@bot.command(name="add_req")
async def add_req(ctx, app, req):
    req = get_id_from_mention(req)
    try:
        guild.get_role(req)
    except HTTPException:
        await ctx.send("Error, could you please re-run the command")
        return
    except NotFound:
        await ctx.send("I am taking only roles as requirements as of now.")
        return
    det = f"{app}_{req}"
    with open(r"config\req.txt") as file:
        if det in str(file.readlines()):
            await ctx.send("This is already a requirement.")
            return
        else:
            with open("req.txt", "a") as file:
                file.write(det)
            await ctx.send(f"Users will now require {return_name_of_role(req)} to apply.")



@bot.command(name="remove_req")
async def remove_req(ctx, app, req):
    req = get_id_from_mention(req)
    try:
        guild.get_role(req)
    except HTTPException:
        await ctx.send("Error, could you please re-run the command")
        return
    except NotFound:
        await ctx.send("I am taking only roles as requirements as of now.")
        return
    det = f"{app}_{req}"
    with open(r"config\req.txt") as file:
        if det not in str(file.readlines()):
            await ctx.send("This was never a requirement.")
            return
        else:
            with open(r"config\req.txt", "r+") as f:
                file_source = f.read()
                f.write(file_source.replace(f"{det}", ""))
            await ctx.send(f"Users will no longer require {return_name_of_role(req)} to apply")

def get_applog():
    with open(r"config/applog.txt") as file:
        return int(file.read())
        
##########################################################################
###################### idk some indentation work for #####################
####################### question category hierarchy ######################
##########################################################################
@bot.command(name="write_hier")
async def write_hier(ctx):
    if str(ctx.message).replace("`", "") != "" or str(ctx.message).replace("`", "") != "\n":
        with open(r"config/hier.txt", "w") as file:
            file.write(str(ctx.message).replace('`', ""))
##########################################################################
############### Can The User Apply Check Functions Support ###############
################ I'm Too Lazy To Put Them In Real Function ###############
##########################################################################

def get_reqs(app):
    some_temp_list = []
    with open(r"config\req.txt") as file:
        ah = file.readlines()
        for ahi in ah:
            if f"{app}_" in ahi:
                some_temp_list.append(int(ahi.split("_")[-1]))
    return some_temp_list

def get_role_blacklists(app):
    some_temp_list = []
    with open(r"bl\blacklists.txt") as file:
        ah = file.readlines()
        for ahi in ah:
            if f"{app}_" in ahi:
                some_temp_list.append(int(ahi.split("_")[-1]))
    return some_temp_list

def common_member(a, b):
    return(any(i in a for i in b))

def get_role_ids(usrid):
    usr = bot.fetch_user(usrid)
    roles_ids = []
    for y in usr.roles:
        roles_ids.append(y.id)
    return roles_ids

def get_general_req():
    some_temp_list = []
    with open(r"config\req.txt") as file:
        ah = file.readlines()
        for ahi in ah:
            if "general_" in ahi:
                some_temp_list.append(int(ahi.split("_")[-1]))
    return some_temp_list

def checkInFirst(a, b):
     #getting count
    count_a = Counter(a)
    count_b = Counter(b)
  
    #checking if element exsists in second list
    for key in count_b:
        if key not in  count_a:
            return False
        if count_b[key] > count_b[key]:
            return False
    return True

def get_active():
    with open(r"config\active_apps.txt") as file:
        return file.readlines()

##########################################################################
############### Can The User Apply Check Functions Because ###############
################ I'm Too Lazy To Put Them In Once Function ###############
##########################################################################

def is_user_blacklisted(app, usrid):
    d = f"{app}_{usrid}"
    with open(r"bl\usr_blacklists.txt") as file:
        return d in file.readlines()

def is_role_blacklisted(usrid, app):
    with open(r"bl\rl_blacklists.txt") as file:
        return common_member((get_role_ids(usrid)), get_role_blacklists(app))

def is_any_app_active():
    with open(r"config\active_apps.txt") as file:
        if str(file.read()).replace("\n", "") == "":
            return False
        else:
            return True

def is_app_active(app):
    with open(r"config\active_apps.txt") as file:
        if app in file.read():
            return True
    return False

def meets_general_req(usrid):
    with open(r"config\req.txt") as file:
        checkInFirst(get_role_ids(usrid), get_general_req())

def can_apply_to_any(usrid):
    x = []
    for app in get_active():
        x.append(checkInFirst(get_role_ids(usrid), get_reqs(app)))
    if True in x:
        return True
    else:
        return False

def meets_app_req(usrid, app):
    return checkInFirst((get_role_ids(usrid)), get_reqs(app))

##########################################################################
############################# The Main Stuff #############################
############################# Because Why Not ############################
##########################################################################

async def all_checks(ctx, app):
    usrid = ctx.author.id
    if is_any_app_active():
        if is_app_active(app):
            if meets_general_req(usrid):
                if can_apply_to_any(usrid):
                    if not is_user_blacklisted(app, usrid):
                        if not is_role_blacklisted(usrid, app):
                            if meets_app_req(usrid, app):
                                try:
                                    await ctx.author.send("Starting application... hang on a moment...")
                                    return True
                                except Forbidden:
                                    return("I can't DM you, please make sure your dms are open.")
                                except HTTPException:
                                    return("An error occured, try again later.")
                            return ("You do not meet the requirements to apply to this application")
                        return ("You have a role which is blacklisted from applying")
                    return ("You are blacklisted from applying.")
                return ("There is no application you can apply to")
            return ("You do not meet the general requirements for applying.")
        return ("This application is not accepting applications at the moment.")
    return ("There is no applicationg taking responses right now.")

def emb(title, ques):
    em = discord.Embed(title=title, description=ques)
    em.set_footer("send cancel to cancel your application.")
    return em

def get_hier():
    with open(r"config\hier.txt") as file:
        return file.readlines()
def get_indent(stri):
    return stri.count(" ")

@bot.command(name="apply")
async def apply(ctx, app):
    x = all_checks(ctx, app)
    
    if x != True:
        await ctx.reply(x)
    else:
        await ctx.send("Started application in DMs!")
        answer_embed = discord.Embed(title="Application", description=f"Application of user {ctx.author} for app {app}")
        z = get_hier()
        for i in z():
            if z.index(i) != (len(x)-1) and get_indent(i) != get_indent(i+1):
                x = get_hier()[i].replace(':', '\'\'').replace(" ", "")
                with open(f"questions/{x}.txt") as file:
                    for ques in file.readlines():
                        await ctx.author.send(emb(x, ques))
                        def check(m):
                            return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
                        msg = await bot.wait_for("message", check=check)
                        if msg.content != "cancel":
                            answer_embed.add_field(name=ques, value=msg)
                        else:
                            await ctx.author.send("Cancelled application.")
                            log(f"User {ctx.author} cancelled their application.")
                            return
            elif z.index(i) != (len(x)-1) and get_indent(i) == get_indent(i+1):
                a1 = str(i).replace(":", "").repalce(" ", "")
                a2 = str(i+1).replace(":", "").repalce(" ", "")
                await ctx.author.send(f"Would you like to answer questions for category: {a1} or for category: {a2}\nAnswer with the category name exactly as it appears.")
                def check(m):
                    return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
                msg = await bot.wait_for("message", check=check)
                if msg.content != "cancel":
                    with open(f"questions/{msg.content}.txt") as file:
                        for ques in file.readlines():
                            await ctx.author.send(emb(x, ques))
                            def check(m):
                                return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
                            msg = await bot.wait_for("message", check=check)
                            if msg.content != "cancel":
                                answer_embed.add_field(name=ques, value=msg)
                            else:
                                await ctx.author.send("Cancelled application.")
                                log(f"User {ctx.author} cancelled their application.")
                                return
                else:
                    await ctx.author.send("Cancelled application.")
                    log(f"User {ctx.author} cancelled their application.")
                    return
        bot.get_channel(get_applog).send(answer_embed)
        return




##########################################
######## FORGET ABOUT THIS STUFF #########
##########################################
def restart_bot():
    os.execv(sys.executable, ['python'] + sys.argv)

@bot.command(name="restart")
@commands.is_owner()
async def restart(ctx):
    await ctx.send("Restarting the bot...")
    restart_bot()

@bot.command(name="shutdown")
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("shutting down...")
    await bot.close()

@bot.command()
@commands.is_owner()
async def disable(ctx, command):
    command = bot.get_command(command)
    if not command.enabled:
        return await ctx.send("This command is already disabled.")
    command.enabled = False
    await ctx.send(f"Disabled {command.name} command.")

@bot.command()
@commands.is_owner()
async def enable(ctx, command):
    command = bot.get_command(command)
    if command.enabled:
        return await ctx.send("This command is already enabled.")
    command.enabled = True
    await ctx.send(f"Enabled {command.name} command.")


bot.run(config.token)