import discord
from discord.ext import commands
import random
import asyncio
from cogs.errors import CustomChecks

class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    alias = "Games"

    #now this, ladies and gentlemen, is a mess of if statements
    #but it works :'D
    @commands.command(aliases=['hman', 'hang'], help="play a game of Hangman by yourself or with your friends", usage="hangman @users`[optional]`###30s/user###No")
    @CustomChecks.blacklist_check()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def hangman(self, ctx, members : commands.Greedy[discord.Member]):
        def check(x):   #if the guesses are said by the game participants in the same channel
            return x.author in members and x.channel == ctx.message.channel
        for member in members:  #if the author mentions himself (he will be automatically put in the list) or a bot, remove them from the list
            if member.bot or member == ctx.message.author:
                members.remove(member)
        members.append(ctx.message.author)  #see above
        #these are the images I used
        stages = [
            "https://cdn.discordapp.com/attachments/725102631185547427/752936429356580975/hman10.png",
            "https://cdn.discordapp.com/attachments/725102631185547427/752936398927036436/hman9.png",
            "https://cdn.discordapp.com/attachments/725102631185547427/752936372519567410/hman8.png",
            "https://cdn.discordapp.com/attachments/725102631185547427/752936348561703042/hman7.png",
            "https://cdn.discordapp.com/attachments/725102631185547427/752936324914217041/hman6.png",
            "https://cdn.discordapp.com/attachments/725102631185547427/752936300364955659/hman5.png",
            "https://cdn.discordapp.com/attachments/725102631185547427/752936278407905341/hman4.png",
            "https://cdn.discordapp.com/attachments/725102631185547427/752936254810619935/hman3.png",
            "https://cdn.discordapp.com/attachments/725102631185547427/752936237240680628/hman2.png",
            "https://cdn.discordapp.com/attachments/725102631185547427/752936227010904114/hman1.png",
            "https://cdn.discordapp.com/attachments/725102631185547427/752938893036486776/hman0.png"
        ]
        chances = 10    #these are the chances that the players are getting
        tried_cases = []    #every guess will be kept here
        #this will be the string the tried_cases list will be formatted
        _cases = '** **'    #the default value is a trick because embed fields cannot have spaces as values (thx doggo <3)
        aux_embed = discord.Embed(color=random.randint(0, 0xffffff))    #this is an auxiliary embed
        word = random.choice(list(open('./text files/hang.txt', encoding='utf8')))  #get a random word from the text file
        #create the game embed
        embed = discord.Embed(title='Hangman', color=random.randint(0, 0xffffff))
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/725102631185547427/752936429356580975/hman10.png')
        embed.set_image(url=stages[10])
        embed.set_footer(icon_url=self.bot.user.avatar_url, text='Respond with letters or words. Type "end" or "leave" to leave the game.')
        hidden_word = []    #this is a list that will contain all the characters in the word
        word = word.replace('\n', '')   #it seems that '\n' counts as a word character too (learned it the hard way) so it will get deleted
        for x in word:  #add every character of the word in the list
            hidden_word.append(x)
        for x in range(1, len(hidden_word)-1):  #replace every character in the list with ' ??? ', except the first and the last one, for obvious reasons
            hidden_word[x] = ' ??? '
        embed.description = ''.join(hidden_word)    #format the character list
        embed.description = f'**{embed.description}**\n\n**Chances**: {chances}\n\n**Already Tried**: {_cases}' #set the description of the embed
        await ctx.send(embed=embed) #send the first game embed
        while chances > 0:  #while the players still have chances
            if len(members) > 0:    #if there are players left
                try:    #wait for responses from the players
                    guess = await self.bot.wait_for('message', check=check, timeout=20)
                    _guess = guess.content.upper()
                #except the timeout
                #if somebody doesn't respond in time all players lose the game
                except asyncio.TimeoutError:
                    embed.set_author(icon_url=self.bot.user.avatar_url, name="Time's out. You're dead :(")
                    embed.description = f'**{word}**\n\n**Chances**: {chances}\n\n**Already Tried**: {_cases}'
                    embed.set_footer(text='Better luck escaping hanging next time.', icon_url=self.bot.user.avatar_url)
                    embed.set_image(url=stages[0])
                    return await ctx.send(embed=embed)
                if _guess == 'END' or _guess == 'LEAVE':    #if someone types "leave" or "end"
                    if len(members) > 1:    #if there is more than one player
                        members.remove(guess.author)    #remove him from the players list
                        aux_embed.set_author(icon_url=guess.author.avatar_url, name='Member Left')
                        aux_embed.description = guess.author.mention
                        aux_embed.set_thumbnail(url=stages[0])
                        aux_embed.set_footer(icon_url=self.bot.user.avatar_url, text="Hope you had fun hanging around.")
                        await ctx.send(embed=aux_embed)
                    else:   #if there is only one player, end the game
                        aux_embed.set_author(icon_url=self.bot.user.avatar_url, name='Game Ended')
                        aux_embed.set_thumbnail(url=stages[0])
                        aux_embed.description = f'**{word}**\n\n**Chances**: {chances}\n\n**Already Tried**: {_cases}'
                        aux_embed.set_image(url=stages[0])
                        aux_embed.set_footer(icon_url=self.bot.user.avatar_url, text="Hope you had fun hanging around.")
                        return await ctx.send(embed=aux_embed)
                elif _guess == word:    #if someone guessed the word
                    embed.set_author(icon_url=self.bot.user.avatar_url, name='You Won!')
                    embed.description = f'**{word}**\n\n**Chances**: {chances}\n\n**Already Tried**: {_cases}'
                    embed.set_footer(text='Congrats!', icon_url=self.bot.user.avatar_url)
                    embed.set_image(url='https://cdn.discordapp.com/attachments/725102631185547427/726574014037753886/190614-Award-nominations-iStock-1002281408.png')
                    return await ctx.send(embed=embed)
                elif _guess != 'END' or _guess != 'LEAVE':  #if the guess entry is not 'end' or 'leave'
                    if _guess not in tried_cases:   #and if the guess was not said before
                        tried_cases.append(_guess)  #add it to the already tried cases
                        _cases = ', '.join(tried_cases) #format the list in a string to be added in the description
                    else:   #if the guess was already said before
                        aux_embed.set_author(icon_url=self.bot.user.avatar_url, name='Already Tried')
                        aux_embed.set_thumbnail(url=stages[0])
                        aux_embed.description = 'You already tried that.'
                        aux_embed.set_footer(icon_url=self.bot.user.avatar_url, text='Pay more attention next time.')
                        await ctx.send(embed=aux_embed)
                    if len(_guess) == 1:    #if the guess is only a letter
                        if _guess not in word:  #if the guess is not in the word
                            chances -= 1    #decrease the chances left
                            #update the embed
                            embed.description = ''.join(hidden_word)
                            embed.description = f'**{embed.description}**\n\n**Chances**: {chances}\n\n**Already Tried**: {_cases}'
                            embed.set_image(url=stages[chances])
                            if chances == 0:    #if the players don't have any chances left
                                embed.set_author(icon_url=self.bot.user.avatar_url, name="You're dead :(")
                                embed.description = f'**{word}**\n\n**Chances**: {chances}\n\n**Already Tried**: {_cases}'
                                embed.set_footer(text='Better luck escaping hanging next time.', icon_url=self.bot.user.avatar_url)
                            await ctx.send(embed=embed)
                        else:   #if the guess is in the word
                            for x in range(0, len(word)):   #for every character in the word equal to the guess
                                if _guess == word[x]:
                                    hidden_word[x] = _guess #reveal the letter
                            embed.description = ''.join(hidden_word)    #fomat the updated list to a string
                            if embed.description == word:   #the game ends if the string is equal with the word
                                embed.set_author(icon_url=self.bot.user.avatar_url, name='You Won!')
                                embed.description = f'**{word}**\n\n**Chances**: {chances}\n\n**Already Tried**: {_cases}'
                                embed.set_footer(text='Congrats!', icon_url=self.bot.user.avatar_url)
                                embed.set_image(url='https://cdn.discordapp.com/attachments/725102631185547427/726574014037753886/190614-Award-nominations-iStock-1002281408.png')
                                return await ctx.send(embed=embed)
                            #update the embed
                            embed.description = f'**{embed.description}**\n\n**Chances**: {chances}\n\n**Already Tried**: {_cases}'
                            embed.set_image(url=stages[chances])
                            await ctx.send(embed=embed)
                    else:   #if the guess is not a letter and is wrong
                        chances -= 1    #decrease the chances left
                        #update the embed
                        embed.description = ''.join(hidden_word)
                        embed.description = f'**{embed.description}**\n\n**Chances**: {chances}\n\n**Already Tried**: {_cases}'
                        embed.set_image(url=stages[chances])
                        if chances == 0:    #if the players don't have any chances left
                            embed.set_author(icon_url=self.bot.user.avatar_url, name="You're dead :(")
                            embed.description = f'**{word}**\n\n**Chances**: {chances}\n\n**Already Tried**: {_cases}'
                            embed.set_footer(text='Better luck escaping hanging next time.', icon_url=self.bot.user.avatar_url)
                        await ctx.send(embed=embed)

    #guess the number game
    #todo I should make a hint system
    @commands.command(help="guess a random number", usage="guess <limit>`[optional]`###3s/user###No")
    @CustomChecks.blacklist_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def guess(self, ctx, number: int = 10):
        if number < 10:
            if number < 2:
                return await ctx.send('Not a valid number.')    #if the number chose is under less than 2 it's not considered a valid number
            return await ctx.send("It'd be too easy, don't you think?")    #let's not make the game that easy
        if number == 10:    #by default, if no number is specified by the command author, a number between 1 and 10 will be chosen
            chances = 3    #this is the number of tries a user has
            a = 0
        else:   #if the number is bigger than 10, increase the chances (needs to be reworked a little)
            a = 0
            copy = number
            while copy > 10:
                copy -= 10
                a += 1
            chances = a*2+3
        embed = discord.Embed(title=f'Guess a number between **1** and **{number}**.', description=f'`{chances}` chances left.', color=random.randint(0, 0xffffff))
        embed.set_author(icon_url=ctx.message.author.avatar_url, name=ctx.message.author)
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/725102631185547427/750763651761438810/guess.png')
        embed.set_footer(icon_url=self.bot.user.avatar_url, text='Type "end" to end the game.')
        await ctx.send(embed=embed)
        def check(x):   #check if the response was sent in the same channel by the same user 
            return x.author == ctx.message.author and x.channel == ctx.message.channel
        answer = random.randint(1, number)  #picks the answer
        responses = [] #initialize an empty list to store the responses
        while chances > 0:  #while the user still has chances
            chances -= 1    #decrease the number of tries
            try:
                guess = await self.bot.wait_for('message', check=check, timeout=20)    #wait for the response
                if not guess.content.isdigit(): #if the response is not an integer
                    if str(guess.content).lower() != 'end': #and if the response is not 'end'
                        await ctx.send('Not a valid response.')
                        chances += 1
                        continue    #continues the operations (had an issue where the code was blocking and had to use it for maintaining the flow)
                else:
                    responses.append(guess)
            except asyncio.TimeoutError:    #if the wait_for times out notify the user and return
                embed.description = f'You took to long to respond. The answer was **{answer}**.'
                embed.set_footer(icon_url=self.bot.user.avatar_url, text='Good luck next time.')
                return await ctx.send(embed=embed)
            if chances == 0 and int(guess.content) != answer:   #break if the user has no more chances and did not give the right answer
                embed.description = f'That was your last try.\nThe answer was **{answer}**.'
                embed.set_footer(icon_url=self.bot.user.avatar_url, text='Good luck next time.')
                await ctx.send(embed=embed)
                break
            elif str(guess.content).lower() == 'end':   #break if the user types 'end'
                embed.description = f'Game ended.\nThe answer was **{answer}**.'
                embed.set_footer(icon_url=self.bot.user.avatar_url, text='Good luck next time.')
                await ctx.send(embed=embed)
                break
            elif int(guess.content) == answer:  #break if the user guessed the right number
                embed.description = f':tada: ***Congrats! You won!*** :confetti_ball:'
                embed.set_footer(icon_url=self.bot.user.avatar_url, text='What a psychic.')
                await ctx.send(embed=embed)
                break
            elif int(guess.content) < answer:   #indications
                embed.description = f'***Nope.*** **Go higher.**\n`{chances}` chances left.'
                embed.set_footer(icon_url=self.bot.user.avatar_url, text="C'mon... Read my robo-mind...")
                await ctx.send(embed=embed)
            elif int(guess.content) > answer:
                embed.description = f'***Nope.*** **Go lower.**\n`{chances}` chances left.'
                embed.set_footer(icon_url=self.bot.user.avatar_url, text="C'mon... Read my robo-mind...")
                await ctx.send(embed=embed)
    
    @commands.command(aliases=['rps'], help="duel with someone in the ultimate battle", usage="rps <choice> @user###3s/user###No")
    @CustomChecks.blacklist_check()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def rockpaperscissors(self, ctx, choice: str=None, member: discord.Member=None):
        choice_list = ['rock', 'paper', 'scissors']
        embed = discord.Embed(title='**Rock**-**Paper**-**Scissors**', color=random.randint(0, 0xffffff))
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/725102631185547427/750789031134232758/rps.png')
        if not choice:  #if no choice is made invoking the command
            embed.description = 'Choose your weapon first.'
            embed.set_footer(icon_url=self.bot.user.avatar_url, text='"rock"/"paper"/"scissors"')
            embed.set_author(icon_url=ctx.message.author.avatar_url, name=ctx.message.author)
            return await ctx.send(embed=embed)
        elif choice.lower() not in choice_list:   #if it's not a valid choice
            embed.description = 'Not a valid choice. Choose between **rock**-**paper**-**scissors**.'
            embed.set_footer(icon_url=self.bot.user.avatar_url, text="Let's keep it basic and not play with lasers and guns.")
            embed.set_author(icon_url=ctx.message.author.avatar_url, name=ctx.message.author)
            return await ctx.send(embed=embed)
        if not member:  #if no one is mentioned
            embed.description = 'Mention someone to duel with.'
            embed.set_footer(icon_url=self.bot.user.avatar_url, text='You could try and play with yourself irl tho (and no, not that way).')
            embed.set_author(icon_url=ctx.message.author.avatar_url, name=ctx.message.author)
            return await ctx.send(embed=embed)
        if member.bot:  #bots won't respond
            embed.description = "You can't play with bots. They'll destroy you."
            embed.set_footer(icon_url=self.bot.user.avatar_url, text="Or ignore you. We're busy things.")
            embed.set_author(icon_url=ctx.message.author.avatar_url, name=ctx.message.author)
            return await ctx.send(embed=embed)
        await ctx.message.delete()  #delete the message sent initially so the challenged user does not see the choice made by the author
        embed.description = f'{ctx.message.author.mention} **provoked you to the ultimate duel, make your choice.**'
        embed.set_author(icon_url=member.avatar_url, name=member)
        embed.set_footer(icon_url=self.bot.user.avatar_url, text='Respond with "rock"/"paper"/"scissors" to the duel.')
        await ctx.send(embed=embed)
        await ctx.send(member.mention)
        def check(x): #check if the response was given only by the challenged user
            return x.author == member and x.channel == ctx.message.channel
        try:
            member_choice = await self.bot.wait_for('message', check=check, timeout=20) #wait for the response
            a = choice.lower()
            b = member_choice.content.lower()
            #after lowering both choices the tests are made and the final result gets a value
            if b not in choice_list:
                embed.description = 'Not a valid choice. Choose between **rock**-**paper**-**scissors** next time.'
                embed.set_footer(icon_url=self.bot.user.avatar_url, text="Let's keep it basic and not play with lasers and guns.")
                embed.set_author(icon_url=member.avatar_url, name=member)
            if (a == 'rock' and b == 'scissors'):
                embed.set_author(icon_url=self.bot.user.avatar_url, name='End of the battle')
                embed.description = f':mountain: **Rock wins!**\n**Congrats** {ctx.message.author.mention}!'
                embed.set_footer(icon_url=self.bot.user.avatar_url, text=f'{member} was defetead.')
            elif (b == 'rock' and a == 'scissors'):
                embed.set_author(icon_url=self.bot.user.avatar_url, name='End of the battle')
                embed.description = f':mountain: **Rock wins!**\n**Congrats** {member.mention}!'
                embed.set_footer(icon_url=self.bot.user.avatar_url, text=f'{ctx.message.author} was defetead.')
            elif (a == 'paper' and b == 'rock'):
                embed.set_author(icon_url=self.bot.user.avatar_url, name='End of the battle')
                embed.description = f':page_facing_up: **Paper wins!**\n**Congrats** {ctx.message.author.mention}!'
                embed.set_footer(icon_url=self.bot.user.avatar_url, text=f'{member} was defetead.')
            elif (b == 'paper' and a == 'rock'):
                embed.set_author(icon_url=self.bot.user.avatar_url, name='End of the battle')
                embed.description = f':page_facing_up: **Paper wins!**\n**Congrats** {member.mention}!'
                embed.set_footer(icon_url=self.bot.user.avatar_url, text=f'{ctx.message.author} was defetead.')
            elif (a == 'scissors' and b == 'paper'):
                embed.set_author(icon_url=self.bot.user.avatar_url, name='End of the battle')
                embed.description = f':scissors: **Scissors win!**\n**Congrats** {ctx.message.author.mention}!'
                embed.set_footer(icon_url=self.bot.user.avatar_url, text=f'{member} was defetead.')
            elif (b == 'paper' and a == 'scissors'):
                embed.set_author(icon_url=self.bot.user.avatar_url, name='End of the battle')
                embed.description = f':scissors: **Scissors win!**\n**Congrats** {member.mention}!'
                embed.set_footer(icon_url=self.bot.user.avatar_url, text=f'{ctx.message.author} was defetead.')
            elif a == b:
                embed.set_author(icon_url=self.bot.user.avatar_url, name='End of the battle')
                embed.description = ":crossed_swords: **It's a tie!**"
                embed.set_footer(icon_url=self.bot.user.avatar_url, text='What a fight.')
        except asyncio.TimeoutError:    #if the time runs out and the mentioned user did not respond return
            embed.set_author(icon_url=self.bot.user.avatar_url, name='End of the battle')
            embed.description = f"{member.mention} chose silence..."
            embed.set_footer(icon_url=self.bot.user.avatar_url, text='Better luck next time.')
            return await ctx.send(embed=embed)
        await ctx.send(embed=embed)  #send the embed
    
    @commands.command(aliases=['tod'], help="play Truth or Dare with your friends", usage="tod###2s/user###No")
    @CustomChecks.blacklist_check()
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def truthordare(self, ctx):
        def check(x):   #checks if the response is sent by the command author in the same channel where the command was invoked
            return x.author == ctx.message.author and x.channel == ctx.message.channel
        color = random.randint(0, 0xffffff)
        embed = discord.Embed(color=color, title='Truth or Dare?')
        embed.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/725102631185547427/740536681437855824/truthordare.png')
        embed.set_footer(icon_url=self.bot.user.avatar_url, text='Respond with "truth", "t", "dare", "d".')
        await ctx.send(embed=embed)
        try:
            choice = await self.bot.wait_for('message', check=check, timeout=20)    #wait for the response
            if str(choice.content).lower() != 'truth' and str(choice.content).lower() != 'dare' and str(choice.content).lower() != 't' and str(choice.content).lower() != 'd':
                await ctx.send('Not a valid choice.')
        except asyncio.TimeoutError:    #if the wait_for times out return and notify the user
            return await ctx.send(f'{ctx.message.author.mention} you took to long to respond.')
        if str(choice.content).lower() == 'truth' or str(choice.content).lower() == 't':
            response = random.choice(list(open('./text files/truth.txt')))
            thumbnail = 'https://cdn.discordapp.com/attachments/725102631185547427/740536728699404359/truth.png'
        elif str(choice.content).lower() == 'dare' or str(choice.content).lower() == 'd':
            response = random.choice(list(open('./text files/dare.txt')))
            thumbnail = 'https://cdn.discordapp.com/attachments/725102631185547427/740536746990633001/dare.png'
        embed = discord.Embed(color=color, title=response)
        embed.set_author(name=ctx.message.author, icon_url=ctx.message.author.avatar_url)
        embed.set_thumbnail(url=thumbnail)
        await ctx.send(embed=embed)

    #flip a coin
    @commands.command(help="flip a coin", usage="flip###1s/user###No")
    @CustomChecks.blacklist_check()
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def flip(self, ctx):
        responses = ['heads','tails']
        choice = random.choice(responses)
        if choice == 'heads':            
            cap = discord.Embed(title='Heads', color=0x36393E)
            cap.set_image(url='https://cdn.discordapp.com/attachments/725102631185547427/725102815768215602/cap.png')
            await ctx.send(embed=cap)
        else:
            pajura = discord.Embed(title='Tails', color=0x36393E)
            pajura.set_image(url='https://cdn.discordapp.com/attachments/725102631185547427/725102825109061712/pajura.png')
            await ctx.send(embed=pajura)

    #roll the dices
    #todo maybe I'll further develop this command too
    @commands.command(aliases=['dice', 'dices'], help="roll the dices", usage="roll###1s/user###No")
    @CustomChecks.blacklist_check()
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def roll(self, ctx):
        number = random.randint(1, 12)
        embed = discord.Embed(title=f'You rolled **__{number}__**', color=random.randint(0, 0xffffff))
        embed.set_author(icon_url=ctx.message.author.avatar_url, name=ctx.message.author)
        embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/725102631185547427/735245591872798810/dice.png')
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Games(bot))