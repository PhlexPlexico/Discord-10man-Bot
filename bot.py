import asyncio
import discord
import myToken
import random

#loads of vars we'll need to persist
client = discord.Client()
ourServer = None
inProgress = False
readyUsers = []
firstCaptain = None
secondCaptain = None
teamOne = []
teamTwo = []
currentPickingCaptain = ""
pickNum = 1
team1VoiceChannel = None
team2VoiceChannel = None
serverName = myToken.guildID

@client.event
async def on_ready():
    global ourServer
    global team1VoiceChannel
    global team2VoiceChannel

    team1VoiceChannel = client.get_channel(myToken.team1ChannelId)
    team2VoiceChannel = client.get_channel(myToken.team2ChannelId) 
    print('------')    
    print('Logged in as {} with id {}'.format(client.user.name, client.user.id))
    print('VC1 Name is {}\nVC2 Name is {}'.format(team1VoiceChannel, team2VoiceChannel))
    print('------')    
    #loop over all the servers the bots apart
    

@client.event
async def on_message(message):
    #we received a message
    #modifying these globals
    global inProgress
    global readyUsers
    global firstCaptain
    global secondCaptain
    global teamOne
    global teamTwo
    global pickNum

    #extract the author from the message
    author = message.author

    #make sure they're using the bot setup channel
    if(message.channel.id != myToken.setupChannelId): 
        #if they aren't using an appropriate channel, return
        return

    #ready command
    if (message.content == '!gaben' or message.content == '!ready') and inProgress == False and len(readyUsers) < 10:        
        #check if they are already ready
        if(author in readyUsers):            
            await message.channel.send("You're already ready, chill.")
            return
        #actually readying up
        else:
            #add them to the ready list and send a message
            readyUsers.append(author)
            if(len(readyUsers) == 8 or len(readyUsers) == 9):
                await message.channel.send("<@&" + str(myToken.csRoleID) + ">" + " we only need " + str(10 - len(readyUsers)) + " COME AND JOIN AND HAVE A GOOD TIME!")
            elif(len(readyUsers) == 10):
                #we have 10 ready users, now need captains
                await message.channel.send("WE BALLIN'. Now randomly selecting captains.")
                inProgress = True
                firstCaptain = readyUsers[random.randrange(len(readyUsers))]
                readyUsers.remove(firstCaptain)
                secondCaptain = readyUsers[random.randrange(len(readyUsers))]
                readyUsers.remove(secondCaptain)
                await message.channel.send("First captain is now " + firstCaptain.mention + ". Second captain is now " + secondCaptain.mention)
                await message.channel.send(firstCaptain.name + " it is now your pick, pick with !pick @user. Please choose from " + " ".join(str(x.mention) for x in readyUsers))
            elif(len(readyUsers) != 0):
                await message.channel.send(author.mention + " is now ready, we need " + str(10 - len(readyUsers)) + " more")
            return
        
    #pick command
    elif (message.content.startswith('!pick') and inProgress == True and pickNum < 9):
        #make sure a captain is picking, and its his turn
        if author == firstCaptain and (pickNum == 1 or pickNum == 4 or pickNum == 6 or pickNum == 8):
            #get the user they picked
            if(len(message.mentions) != 1):
                await message.channel.send("Please pick a user by @ing them. !pick @user")
                return

            pickedUser = message.mentions[0]
            #make sure hes a real user
            if(pickedUser not in (name for name in readyUsers)):
                await message.channel.send(str(pickedUser) + " is not in the 10man, please pick again.")
                return

            #add him to team one
            teamOne.append(pickedUser)

            #move him to voice channel for team 1
            await pickedUser.move_to(team1VoiceChannel)
            
            #remove him from ready users
            readyUsers.remove(pickedUser)     

            #increment pick number
            pickNum+=1

            #check if we're done picking
            if(pickNum == 8):
                message = '''The teams are now made and bot setup is finished.
                
                Team 1: ''' + ", ".join(sorted(str(x.name) for x in teamOne)) + '''
                
                Team 2: ''' + ", ".join(sorted(str(x.name) for x in teamTwo)) + '''

                Good luck and have fun!'''

                await message.channel.send(message)
                inProgress = False
                readyUsers = []
                firstCaptain = None
                secondCaptain = None
                pickNum = 1
                return
            #check if we need to pick again or its other captains turn
            if(pickNum == 2 or pickNum == 3 or pickNum == 5 or pickNum == 7):
                await message.channel.send(secondCaptain.mention + " it is now your pick, pick with !pick user. Please choose from " + " ".join(str(x.mention) for x in readyUsers))
            else:
                await message.channel.send(firstCaptain.mention + " please pick again from" + " ".join(str(x.mention) for x in readyUsers))

        #similar to above, just for team 2 and captain 2
        elif author == secondCaptain and (pickNum == 2 or pickNum == 3 or pickNum == 5 or pickNum == 7):
            #get the user they picked
            if(len(message.mentions) != 1):
                await message.channel.send("Please pick a user by @ing them. !pick @user")
                return

            pickedUser = message.mentions[0]
            teamTwo.append(pickedUser)
            
            #move him to voice channel for team 2
            await pickedUser.move_to(team2VoiceChannel)

            #remove him from ready users
            readyUsers.remove(pickedUser)    

            pickNum+=1
            if(pickNum == 1 or pickNum == 4 or pickNum == 6 or pickNum == 8):
                await message.channel.send(firstCaptain.mention + " it is now your pick, pick with !pick user. Please choose from " + " ".join(str(x.mention) for x in readyUsers))
            else:
                await message.channel.send(secondCaptain.mention + " please pick again from" + " ".join(str(x.mention) for x in readyUsers))

        else:
            await message.channel.send("You're not a captain, sorry, but please let the captains select!")
        return

    #unready command               
    elif (message.content == '!unready' or message.content == '!ungaben' and inProgress == False):
        #make sure the user exists
        for user in readyUsers:
            if user == author:
                readyUsers.remove(user)
                #unready message
                await message.channel.send(author.mention + " You are no longer ready. We now need " + str(10 - len(readyUsers)) + " more")            
                break
        return

    #stopping one        
    elif message.content == '!done':
        inProgress = False
        readyUsers = []
        firstCaptain = None
        secondCaptain = None
        pickNum = 1
        await message.channel.send("Current 10man finished, to make a new one, we need 10 ready users")    
        return
    
    elif message.content.startswith('!whosready'):
        if (len(readyUsers) == 0):
            await message.channel.send("There is currently no players in queue!")
        else:
            await message.channel.send(", ".join(sorted(str(x.name) for x in readyUsers)))
        return

client.run(myToken.token)
