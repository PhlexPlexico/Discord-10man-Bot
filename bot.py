import discord
import asyncio
import myToken
from pprint import pprint

#loads of vars we'll need to persist
client = discord.Client()
ourServer = None
inProgress = False
readyUsers = []
firstCaptain = ""
secondCaptain = ""
teamOne = []
teamTwo = []
currentPickingCaptain = ""
pickNum = 1
team1VoiceChannel = None
team2VoiceChannel = None

serverName = "10 men"

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
    t = iter(client.servers)        
    for server in t:            
        #we're trying to find one that has serverName (line 20)
        if(server.name == serverName):            
            #found it, lets hold on to it for later
            ourServer = server
            #In this server, hold on the voice channels for team 1 and team 2 for moving purposes later
            for channel in ourServer.channels:
                if channel.name == "Team 1":
                    team1VoiceChannel = channel
                elif channel.name == "Team 2":
                    team2VoiceChannel = channel
                elif channel.name== "general":
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
    author = str(message.author).split("#")[0]

    #make sure they're using either our testchannel or bot setup channel
    if(message.channel.name != "testchannel" and message.channel.name != "bot-setup" and message.content.startswith("!")):
        #if they aren't using an appropriate channel, send a message and return
        await client.send_message(message.channel, "Please use the bot-setup channel")
        return    

    #ready command
    if (message.content.startswith("!gaben") or message.content.startswith('!ready')) and inProgress == False and len(readyUsers) < 10:        
        #check if they are already ready
        if(author in readyUsers):            
            await client.send_message(message.channel, "You're already ready, chill")
        #actually readying up
        else:
            #add them to the ready list and send a message
            readyUsers.append(author)

            if(len(readyUsers) == 8 or len(readyUsers) == 9):
                it = iter(ourServer.members)
                message = ""
                for user in it:
                    if(str(user.status) == "online" and user.name != "DAD Scrim BOT" and user.name not in readyUsers):
                        message = message + " @" + user.name
                        await client.send_message(message.channel, message + " we only need " + 10 - len(readyUsers) + " PLS READY UP")
            await client.send_message(message.channel, author + " is now ready, we need " + str(10 - len(readyUsers)) + " more")
            elif(len(readyUsers) == 3):
                #we have 10 ready users, now need captains
                await client.send_message(message.channel, "we ready boiz. Please pick two captains by doing !captains captain1 captain2")
                inProgress = True

    #captains command
    elif (message.content.startswith('!captains') and inProgress == True):
        #make sure we dont already have captains
        if (firstCaptain != "" and secondCaptain != ""):
            await client.send_message(message.channel, "We already have captains. To change them do !done and start over")
            return

        #get the first and second captains, remove them from the ready list
        firstCaptain = message.content.split(" ",1)[1].split()[0]
        secondCaptain = message.content.split(" ",1)[1].split()[1]
        readyUsers.remove(firstCaptain)
        readyUsers.remove(secondCaptain)
        #send a message about captains and picks
        await client.send_message(message.channel, "First captain is now " + firstCaptain + ". Second captain is now " + secondCaptain)
        await client.send_message(message.channel, firstCaptain + " it is now your pick, pick with !pick user. Please choose from " + " ".join(readyUsers))
        
    #pick command
    elif (message.content.startswith('!pick') and inProgress == True and pickNum < 10):
        #make sure a captain is picking, and its his turn
        if author.upper() == firstCaptain.upper() and (pickNum == 1 or pickNum == 4 or pickNum == 6 or pickNum == 8):
            #get the user they picked
            pickedUser = message.content.split(" ",1)[1]
            #make sure hes a real user
            if(pickedUser.upper() not in (name.upper() for name in readyUsers)):
                await client.send_message(message.channel, pickedUser + " is not a real user, please pick again")
                return

            #add him to team one
            teamOne.append(pickedUser)

            #move him to voice channel for team 1
            it = iter(ourServer.members)
            for user in it:          
                if(user.name.split("#")[0].upper() == pickedUser.upper()):
                    await client.move_member(user,team1VoiceChannel)
                    break
            
            #remove him from ready users
            for temp in readyUsers:
                if temp.upper() == pickedUser.upper():
                    readyUsers.remove(temp)
                    break       

            #increment pick number
            pickNum+=1

            #check if we're done picking
            if(pickNum == 10):
                await client.send_message(message.channel, "The teams are now made and bot setup is finished.")
                inProgress = False
                readyUsers = []
                firstCaptain = ""
                secondCaptain = ""
                pickNum = 1
                return
            #check if we need to pick again or its other captains turn
            if(pickNum == 2 or pickNum == 3 or pickNum == 5 or pickNum == 7 or pickNum == 9):
                await client.send_message(message.channel, secondCaptain + " it is now your pick, pick with !pick user. Please choose from " + " ".join(readyUsers))
            else:
                await client.send_message(message.channel, firstCaptain + " please pick again from" + " ".join(readyUsers))

        #similar to above, just for team 2 and captain 2
        else if author.upper() == secondCaptain.upper() and (pickNum == 2 or pickNum == 3 or pickNum == 5 or pickNum == 7):
            pickedUser = message.content.split(" ",1)[1]
            if(pickedUser.upper() not in (name.upper() for name in readyUsers)):
                await client.send_message(message.channel, pickedUser + " is not a real user, please pick again")
                return
            teamTwo.append(pickedUser)
            
            it = iter(ourServer.members)
            for user in it:          
                if(user.name.split("#")[0].upper() == pickedUser.upper()):
                    await client.move_member(user,team2VoiceChannel)
                    break

            for temp in readyUsers:
                if temp.upper() == pickedUser.upper():
                    readyUsers.remove(temp)
                    break    

            pickNum+=1
            if(pickNum == 10):
                await client.send_message(message.channel, "The teams are now made and bot setup is finished.")
                inProgress = False
                readyUsers = []
                firstCaptain = ""
                secondCaptain = ""
                pickNum = 1
                return
            if(pickNum == 1 or pickNum == 4 or pickNum == 6 or pickNum == 8 or pickNum == 10):
                await client.send_message(message.channel, firstCaptain + " it is now your pick, pick with !pick user. Please choose from " + " ".join(readyUsers))
            else:
                await client.send_message(message.channel, secondCaptain + " please pick again from" + " ".join(readyUsers))

        else:
            await client.send_message(message.channel, "You're not a captain, sorry")

    #unready command               
    elif (message.content.startswith('!unready') or message.content.startswith('!ungaben')) and inProgress == False:
        #make sure the user exists
        for user in readyUsers:
            if user.upper() == author.upper():
                readyUsers.remove(user)
                #unready message
                await client.send_message(message.channel, author + " You are no longer ready. We now need " + str(10 - len(readyUsers)) + " more")            
                break

    #stopping one        
    elif message.content.startswith('!done'):
        inProgress = False
        readyUsers = []
        firstCaptain = ""
        secondCaptain = ""
        pickNum = 1
        await client.send_message(message.channel, "Current 10man finished, to make a new one, we need 10 ready users")    
    
    elif message.content.startswith('!whosready'):
        await client.send_message(message.channel, " ".join(readyUsers))


client.run(myToken.token)
