import discord
import asyncio
import myToken
from pprint import pprint

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
    global testchannel
    
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')    
    #loop over all the servers the bots apart
    t = iter(client.guilds)        
    for server in t:            
        #we're trying to find one that has serverName (line 20)
        if(server.id == serverName):            
            #found it, lets hold on to it for later
            ourServer = server
            #In this server, hold on the voice channels for team 1 and team 2 for moving purposes later
            for channel in ourServer.channels:
                if channel.id == myToken.team1ChannelId:
                    team1VoiceChannel = channel
                elif channel.id == myToken.team2ChannelId:
                    team2VoiceChannel = channel
                elif channel.id== myToken.setupChannelId:
                    testchannel = channel    

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
    #have to split since it comes in like Meeoh#3282
    author = message.author

    #make sure they're using either our testchannel or bot setup channel
    if(message.channel.id != myToken.setupChannelId and message.content.startswith("!")):
        #if they aren't using an appropriate channel, send a message and return
        await message.channel.send("Please use the setup channel!")
        return    

    #ready command
    if (message.content.startswith("!gaben") or message.content.startswith('!ready')) and inProgress == False and len(readyUsers) < 10:        
        #check if they are already ready
        if(author in readyUsers):            
            await message.channel.send("You're already ready, chill.")
        #actually readying up
        else:
            #add them to the ready list and send a message
            readyUsers.append(author)

            if(len(readyUsers) == 8 or len(readyUsers) == 9):
                await message.channel.send("<@&" + myToken.csRoleID + ">" + " we only need " + 10 - len(readyUsers) + " PLS READY UP")
            elif(len(readyUsers) == 10):
                #we have 10 ready users, now need captains
                await message.channel.send("WE HAWWT. Please pick two captains by doing !captains @captain1 @captain2")
                inProgress = True

            await message.channel.send(author.mention + " is now ready, we need " + str(10 - len(readyUsers)) + " more")


    #captains command
    elif (message.content.startswith('!captains') and inProgress == True):
        #make sure we dont already have captains
        if (firstCaptain != "" and secondCaptain != ""):
            await message.channel.send("We already have captains. To change them do !done and start over")
            return

        #get the first and second captains, remove them from the ready list
        if (len(message.mentions) > 0 and len(message.mentions) < 2):
            await message.channel.send("Please pick two captains!! !captains @captain1 @captain2")
        elif (len(message.mentions) > 2):
            await message.channel.send("Please pick two captains!! !captains @captain1 @captain2")
        elif (len(message.mentions) == 2):
            firstCaptain = message.mentions[0]
            secondCaptain = message.mentions[1]
            readyUsers.remove(firstCaptain)
            readyUsers.remove(secondCaptain)
            #send a message about captains and picks
            await message.channel.send("First captain is now " + firstCaptain.mention + ". Second captain is now " + secondCaptain.mention)
            await message.channel.send(firstCaptain.mention + " it is now your pick, pick with !pick @user. Please choose from " + " ".join(str(x.mention) for x in readyUsers))
        else:
            await message.channel.send("Please pick two captains!! !captains captain1 captain2")
        
    #pick command
    elif (message.content.startswith('!pick') and inProgress == True and pickNum < 10):
        #make sure a captain is picking, and its his turn
        if author == firstCaptain and (pickNum == 1 or pickNum == 4 or pickNum == 6 or pickNum == 8):
            #get the user they picked
            if(len(message.mentions) != 1):
                await message.channel.send("Please pick a user by @ing them. !pick @user")
                return

            pickedUser = message.mentions[0]
            #make sure hes a real user
            if(pickedUser not in (name for name in readyUsers)):
                await message.channel.send(str(pickedUser) + " is not in the 10man, please pick again")
                return

            #add him to team one
            teamOne.append(pickedUser)

            #move him to voice channel for team 1
            pickedUser.move_to(team1VoiceChannel, "Moving for 10man.")
            
            #remove him from ready users
            readyUsers.remove(pickedUser)     

            #increment pick number
            pickNum+=1

            #check if we're done picking
            if(pickNum == 10):
                await message.channel.send("The teams are now made and bot setup is finished. Please create your match at https://get5.phlexplexi.co")
                inProgress = False
                readyUsers = []
                firstCaptain = None
                secondCaptain = None
                pickNum = 1
                return
            #check if we need to pick again or its other captains turn
            if(pickNum == 2 or pickNum == 3 or pickNum == 5 or pickNum == 7 or pickNum == 9):
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
            pickedUser.move_to(team2VoiceChannel, "Moving for 10man.")

            #remove him from ready users
            readyUsers.remove(pickedUser)    

            pickNum+=1
            if(pickNum == 10):
                await message.channel.send("The teams are now made and bot setup is finished.")
                inProgress = False
                readyUsers = []
                firstCaptain = None
                secondCaptain = None
                pickNum = 1
                return
            if(pickNum == 1 or pickNum == 4 or pickNum == 6 or pickNum == 8 or pickNum == 10):
                await message.channel.send(firstCaptain.mention + " it is now your pick, pick with !pick user. Please choose from " + " ".join(str(x.mention) for x in readyUsers))
            else:
                await message.channel.send(secondCaptain.mention + " please pick again from" + " ".join(str(x.mention) for x in readyUsers))

        else:
            await message.channel.send("You're not a captain, sorry")

    #unready command               
    elif (message.content.startswith('!unready') or message.content.startswith('!ungaben')) and inProgress == False:
        #make sure the user exists
        for user in readyUsers:
            if user == author:
                readyUsers.remove(user)
                #unready message
                await message.channel.send(author.mention + " You are no longer ready. We now need " + str(10 - len(readyUsers)) + " more")            
                break

    #stopping one        
    elif message.content.startswith('!done'):
        inProgress = False
        readyUsers = []
        firstCaptain = None
        secondCaptain = None
        pickNum = 1
        await message.channel.send("Current 10man finished, to make a new one, we need 10 ready users")    
    
    elif message.content.startswith('!whosready'):
        await message.channel.send(" ".join(str(x.mention) for x in readyUsers))


client.run(myToken.token)
