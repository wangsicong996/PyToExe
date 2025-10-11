def main():
    current_room = 'PARKING'
    player_inventory = []
    end_status = 'GOOD'
    # extra variable for handling end sequence
    status = 0

    instructionDisplay()
    print('''
    You are an intrepid urban explorer. Last night, you received a strange letter in
    your mailbox. It told you the location of an abandoned Red Lobster seafood restaurant near the
    edge of town. Supposedly, a cryptic accident took place there, but you are unable to find any
    information on it beyond what the letter says. Determined to make it big on your urban explorer
    online forum page, you go to the location marked within the letter.
    You arrive as the sun is just beginning to sink below the horizon. Before you is a derelict building
    with peeling red walls and stained white trim. The sign out front is severely damaged, with the iconic
    lobster and most of the letters long fallen away or stolen. All that remains is the phrase "RedL".
    You get out of your car and walk into the pothole-riddled parking lot.''')

    while current_room != 'END':
        # display text for the player's current room
        displayRoom(current_room, player_inventory, status)

        # handle end sequence
        if current_room == 'OFFICE':
            status = 1

        # allow the player to input choice
        player_choice = input('\nPlease enter a command: ')
        player_choice = player_choice.upper()

        # check if player wants to move areas
        if 'GO TO' in player_choice:
            if current_room == 'PARKING':
                if 'FRONT' in player_choice:
                    print('You walk to the front door. It is made of musty glass covered in cracks.')
                    print('After jostling it several times, you manage to push your way in.')
                    current_room = 'RECEPTION'
                elif 'BACK' in player_choice:
                    print('The back door is covered in red paint and has a gold-rimmed porthole')
                    print('window. It pushes open easily')
                    current_room = 'KITCHEN'
                elif 'WINDOW' in player_choice and 'CROWBAR' in player_inventory:
                    print('You shove the crowbar into the window. Wood splinters and glass buckles')
                    print('as you force your way in.')
                    current_room = 'DINE'
                elif 'WINDOW' in player_choice and 'CROWBAR' not in player_inventory:
                    print('The window appears to be jammed and the glass is too thick to break.')
                    print('You think you could pry it open, but not without a tool.')
                else:
                    print('You cannot go there.')
            elif current_room == 'DINE':
                if 'KITCHEN' in player_choice:
                    print('You open the kitchen doors with ease, briskly stepping inside and shaking')
                    print('the sea water from your boots.')
                    current_room = 'KITCHEN'
                elif 'RECEPTION' in player_choice:
                    print('You enter the reception area, ducking under a stray harpoon lodged in a wall')
                    print('as you go.')
                    current_room = 'RECEPTION'
                elif 'OFFICE' in player_choice:
                    if 'WHALE KEY' in player_inventory:
                        if'CRAB KEY' in player_inventory:
                            if'LOBSTER KEY' in player_inventory:
                                print('The locks clatter into the water as you unlock each of them.')
                                print('The office door swings open with a huanting creak.')
                                print('You enter the dark.')
                                current_room = 'OFFICE'
                    else:
                        print('You walk up to the office door but find it locked.')
                        print('Three padlocks block entry. One made of copper, one made of gold,')
                        print('and one made of ivory. If you want to get the juicy lore of this place,')
                        print('you figure you\'ll need three keys.')
                else:
                    print('You cannot go there.')
            elif current_room == 'RECEPTION':
                if 'DINING' in player_choice:
                    print('You trudge into the dining room, dark water sloshing up around your boots.')
                    current_room = 'DINE'
                else:
                    print('You cannot go there.')
            elif current_room == 'KITCHEN':
                if 'DINING' in player_choice:
                    print('You trudge into the dining room, dark water sloshing up around your boots.')
                    current_room = 'DINE'
                else:
                    print('You cannot go there.')
            elif current_room == 'OFFICE':
                print('There is no going back.')
            else:
                print('No can do.')

        #check if the player wants to search current area
        elif 'SEARCH' in player_choice:
            if current_room == 'PARKING' and 'CROWBAR' not in player_inventory:
                searchRoom(current_room)
                player_inventory.append('CROWBAR')
            elif current_room == 'RECEPTION' and 'LOBSTER KEY' not in player_inventory:
                searchRoom(current_room)
                player_inventory.append('LOBSTER KEY')
            elif current_room == 'KITCHEN' and 'CRAB KEY' not in player_inventory:
                searchRoom(current_room)
                player_inventory.append('CRAB KEY')
            elif current_room == 'DINE' and 'WHALE KEY' not in player_inventory:
                searchRoom(current_room)
                player_inventory.append('WHALE KEY')
            elif current_room == 'OFFICE':
                end_status = 'BAD'
                endGame(end_status)
                break
            else:
                print('There is nothing left to find.')

        # help command check
        elif 'HELP' in player_choice:
            instructionDisplay()

        # for ending choice
        elif 'EXIT' in player_choice and current_room == 'OFFICE':
            endGame(end_status)
            break

        # invalid command
        else:
            print('please input valid command')

# stores and displays instructions
def instructionDisplay():
    print('''
    Hello. Welcome to RedL. In this game you will use basic commands to navigate the story.
    -to inspect and area, write "search" or "search + 'the current area you are in'".
    -to move from place to place, write "go to + 'desired area'"
    -points of interest will be marked in the text with the underline symbol (_area_)
    -when the time is right, type "exit"
    -if you need to read the instruction again, write "help"''')

# stores and displays room description text
def displayRoom(room, inventory, stat):
    if room == 'PARKING':
        print('''
    The parking lot is in bad shape. The lines are near-invisible upon the crumbling asphalt.
    The building beyond seems to have three possible entrances. The _front door_, the _back door_,
    and a cracked _window_ in the building's side. Unfortunately, the window looks like it is inaccessible
    without a tool. There might be something in the _parking lot_ that can help.''')
    elif room == 'RECEPTION':
        print('''
    The decrepit reception area is a musty space of torn carpet and shredded benches. The front kiosk
    is broken entirely in half, a giant harpoon sticking from its side,
    and beyond it the entrance to the _dining room_. Near one end of the room, you see an empty
    lobster tank with its glass fogged up. It has a faint glow within it.''')
    elif room == 'KITCHEN':
        print('''
    Despite its abandonment, the kitchen is alive with inexplicable activity. A pot boils on a rusty stove.
    A clock ticks endlessly above the _dining room_ entrance, its hands unmoving. The freezer whirs,
    and you can hear something clicking inside it.''')
    elif room == 'DINE' and 'WHALE KEY' not in inventory:
        print('''
    The dining room looks like it was hit by a tsunami. The floor is flooded with soupy water, the there
    is a faint smell of fish saturating everything floating in the bile. The very air tastes of salt.
    In the center of sunken furniture, there is a strangely ghost-white booth overturned in the water.
    Many harpoons are stabbed into it, and crimson, yellow-tinged guts pour out of it instead
    of stuffing. You think you can see something inside. Beyond the odd display, there are two exits.
    One marked _kitchen_, and the other clearly leading to a _reception_ area.
    There is also a door that seems to lead into an important looking _office_.''')
    elif room == 'DINE':
        print('''
    The dining room looks like it was hit by a tsunami. The floor is flooded with soupy water, the there
    is a faint smell of fish saturating everything floating in the bile. The very air tastes of salt.
    There are two exits. One marked _kitchen_, and the other clearly leading to a _reception_ area.
    There is also a door that seems to lead into an important looking _office_.''')
    elif room == 'OFFICE' and stat == 0:
      print('''
    As you enter the office, the door slams shut behind you. You turn to find it locked. You are trapped
    in the darkness... but not for long.
    Lights slowly flicker on one by one. The television screens for security cameras. You see all the areas
    you explored, and others you never got the chance to. Hidden backrooms. Impaled on their walls are
    bloated bodies in Red Lobster employee uniforms. Harpoons are shoved through their hearts.
    In the center of the office is a single desk, and floating above it is a man.
    With a long blue coat, a bone-white peg leg, and a scarred face,
    his glowing white eyes fix upon you.
    "I was a fool to kill the whale. I had hunted it so long that I lost everything else. When
    it was dead, I had nothing. No one.
    It drove me mad in life, and madder in death. Here... ye see me final rage.
    Now Hell's heart opens to swallow me whole. Don't take the harpoon, child. Ye will regret it."
    The ghost of Captain Ahab disappears. In his place is the mangled corpse of the manager, a
    harpoon in her heart. It shines gold in the light of many TVs. You imagine that if you _search_
    the room, you can take this valuable artifact with you. Still, the prickly feeling on your neck
    tells you a quick _exit_ may be smarter.''')
    elif room == 'OFFICE':
        print('''
    The mangled corpse of the manager is before you, a
    harpoon lodged in her heart. It shines gold in the light of many TVs. You imagine that if you _search_
    the room, you can take this valuable artifact with you. Still, the prickly feeling on your neck
    tells you a quick _exit_ may be smarter.''')
    print(f'    Inventory: {inventory}')

# store and displays room searching text
def searchRoom(room):
    if room == 'PARKING':
        print('''
You look around, spotting an abandoned hubcap amongst the street trash. At least, you think its a
hubcap until you get a closer look. It is actually what looks to be a ship's steering wheel, and beneath
it you find a hefty crowbar. You imagine you could pry open something with it.''')
    if room == 'RECEPTION':
        print('''
Walking over to the empty lobster tank, you carefully lower your hand into it. You are surprised to find it
is still full of murky water. You slowly reach toward to faint glow, but something brushes your hand. You recoil
but decide to keep going. Deeper and deeper until your whole arm is within the tank. Then... something
grips your arm! You cry out and fall back, only to find the tank empty. Soemthing is in
your hand. A greenish copper key with a lobster modeled on one end. You got the lobster key.''')
    elif room == 'KITCHEN':
        print('''
You slowly approach the freezer. The clicking grows louder as you get closer. You hesitantly reach for the
shining silver handle. You open the towering metal door and...
crabs. Thousands of them. They pour out in an avalanche, covering you. A sea of snapping claws and needle
legs. You feel them tearing at your flesh. Ripping tino tendons and gnawing on bone.
They are coming for your eyes and...
Then they're gone. You are untouched. Only a single crab now stands in the freezer doorway. It holds
up a golden key with a crab symbol molded into it. You take it from the little creature, and it skuttles
into the dark. You got the crab key.''')
    elif room == 'DINE':
        print('''
You trudge up to the torn white booth. You reach into its slimy interior. It is warm and smells
of salt-soaked death. You did deeper and deeper. Bile drips down your arm, soaking the front of your
shirt. You keep going, closing your eyes as the stench overwhelms you.
...
You are no longer in the restaurant. You stand on the beach, a harpoon in your grasp. The corpse
A massive white sperm whale is before you, blood from its torn stomach staining the sand.
Its pearly blue eye turns to look at you. As the light leaves it, you feel sad.
You valued the chase more than the victory.
...
You wake up standing in the dining room. The strange booth is gone. In your hands is an ivory key with
a whale carved into it. You got the whale key.''')

# stores endgame info for final sequence
def endGame(estat):
    if estat == 'BAD':
        print('''
    You approach the fetid body and wrap your hands around the bloodstained gold of the harpoon.
    You pull, the rotting flesh around it creating a sickening noise. It comes out easily, radiant
    like the sun. You hold it, and as you do, one of your legs begins to rot away. Bone grows from the
    bloody stump, forming into a peg leg as you ascend into the air. You smile as you hear a car pull up
    to the building. Moby Dick has arrived.
    BAD ENDING!

    Thanks for playing :)''')
    elif estat == 'GOOD':
        print('''
    The door behind you unlocks with a dull click. You rush out, running for the nearest exit.
    With wet clothes and fear in your heart, you make it to your car and speed away from that acursed
    place. You may not have gotten the big scoop you wanted, but you certainly have a story to tell.
    Good ENDING!

    Thanks for playing :)''')

# calls the main, starting the game
main()
