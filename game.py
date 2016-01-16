# BattleShip game

# Importing required modules

from random import randint
from getch import getch, pause
import string, re, time, sys, os, subprocess

# grab the windows width
win_width = int(subprocess.check_output(['stty', 'size']).split()[1])

# Starting variables
board_size = 0
game_grid = []
letters = "ABCDEFGHI"

ships = []
num_ships = 0
talk_counter = 0
help_counter = 0
about_counter = 0
food_counter = 0
pon_counter = 0
tee_counter = 0
pon_ready = False
tee_ready = False
games_beat = 0
guesses = 0
game_modes = ["default", "hard", ""]
game_mode = "default"

icons = {
    "checkmark": u'\u2713',
    "fill_square": u'\u2588',
}

pon = {
    "neutral": u'[\u25E6_\u25E6]',
    "unsure": u'[\u25E6~\u25E6]',
    "talk": u'[\u25E6\u25B4\u25E6]',
    "otalk": u'[\u25E6o\u25E6]',
    "smiley": u'[\u25E6\u203F\u25E6]',
    "loud": u'[\u25E6\u2596\u25E6]',
    "areyoukidding": u'[\u2256_\u2256]',
    "on_to_you": u'[\u2256\u203F\u2256]',
    "reflect": u'[\u00B0-\u00B0]',
}

tee = {
    "smile": u'(\u02DA\u203F\u02DA)',
    "talk": u'(\u02DA\u25BF\u02DA)',
    "tinysmile": u'(\u02DA\u25E1\u02DA)',
    "wah": u'(\u02DA<\u02DA)',
    "yell": u'(\u02DA\u25B1 \u02DA)',
    "frown": u'(\u02DA\u25B4\u02DA)',
    "sad": u'(\u02DA\u2313 \u02DA)',
    "oh": u'(\u02DA\u25AB\u02DA)',
    "gasp": u'(\u02DA\u25C7\u02DA)',
    "dotdotdot": u'(\u02DA\u23BB\u02DA)',
}

error_text = {
    "pon": ["...could you repeat that.",
            "Im not quite sure I understand.",
            "Try asking something else.",
            "I think you need help with asking for help."],
    "tee": ["I dont get it!",
            "Thats not on the menu!",
            "Maybe another time!",
            "Only on Tuesday."]
}

outcome_text = ["It's a hit!\n", "It's a miss...\n", "You sunk my ship!\n", "You already picked there!\n"]
about_topics_full = ["color", "music", "muffins", "games", "food", "Tee", "Pon", "Jeremy"]
about_topics = ["color", "music", "muffins", "games"]
food_topics = ["favfood", "muffins", "lunch"]


"""""""""""""""
GAME FUNCTIONS

"""""""""""""""

# main function for handling typing text and speech on screen
def text_typer(who, emotion, talkspeed, text, textspeed, delay, newline):
    time.sleep(delay)
    if newline == True:
        print "\n"
    if type(who) == str:
        if who == "Princess" and newline == True:
            sys.stdout.write(tee[emotion] + " ")
        elif who == "Kathy" and newline == True:
            sys.stdout.write(pon[emotion] + " ")
        subprocess.Popen('say -v %s -r %s %s' % (who, talkspeed, text), shell=True)
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(textspeed)

# function to build the battlefield
def grid_setup():
    global board_size
    grid = []
    letter_setup = [" "]

    for x in xrange(board_size):
        letter_setup.append(letters[x])
        grid.append([str(x + 1)] + (["O"] * board_size))

    grid.insert(0, letter_setup)
    return grid

# prints out the current battlefield's status
def show_grid(grid):
    print "Current battlefield:\n"
    for row in grid:
        print " ".join(row)
    print "\n"

# clear the screen function
def clear_screen():
    os.system('clear')
    print "=" * win_width
    sys.stdout.flush()

# function to check if the input is valid
def coord_check(coord):
    global board_size
    match_string = re.compile("^[A-%s][1-%d]$" % (letters[board_size-1], board_size))
    if re.match(match_string, coord, flags=0):
        return True
    else:
        return False

def ship_generator():
    global board_size
    global num_ships
    global ships
    number_of_ships = num_ships
    alignments = ["left", "right", "up", "down"]

    while number_of_ships > 0:
        # if a generation iteration (lol) didn't work then reset variables and try again
        ship_length = randint(2, 5)
        align = 0
        ship_coords = []
        x_y = [randint(1, board_size), randint(1, board_size)]

        # is this number already a coordinate in the ships array?
        if hit_check(x_y, False) == True:
            continue

        # if not, continue!
        ship_coords.append(x_y)

        if x_y[0] - (ship_length - 1) < 1:
            alignments.remove("left")
        if x_y[0] + (ship_length - 1) > board_size:
            alignments.remove("right")
        if x_y[1] - (ship_length - 1) < 1:
            alignments.remove("up")
        if x_y[1] + (ship_length - 1) > board_size:
            alignments.remove("down")

        # if in the rare case that its 5x5 and a 4-length ship is generated in C3
        if len(alignments) == 0:
            alignments = ["left", "right", "up", "down"]
            continue

        align = alignments[randint(0, len(alignments) - 1)]

        for x in xrange(ship_length - 1):
            if align == "up":
                x_y = [ship_coords[x][0], ship_coords[x][1] - 1]
                if hit_check(x_y, False) == True:
                    break
            elif align == "right":
                x_y = [ship_coords[x][0] + 1, ship_coords[x][1]]
                if hit_check(x_y, False) == True:
                    break
            elif align == "down":
                x_y = [ship_coords[x][0], ship_coords[x][1] + 1]
                if hit_check(x_y, False) == True:
                    break
            elif align == "left":
                x_y = [ship_coords[x][0] - 1, ship_coords[x][1]]
                if hit_check(x_y, False) == True:
                    break
            ship_coords.append(x_y)

        if hit_check(x_y, False) == True:
            alignments = ["left", "right", "up", "down"]
            continue

        ships.append({"length": ship_length, "coords": ship_coords})
        if len(alignments) < 4:
            alignments = ["left", "right", "up", "down"]
        number_of_ships -= 1

# checks if the input recieved matches a ship coordinate/duplicate checking
def hit_check(coord_input, striking):
    for ship in ships:
        for xy in ship["coords"]:
            if coord_input == xy:
                if striking == True and ship["length"] > 0:
                    ship["length"] -= 1
                return True

# function to run when guessing coordinates
def hit_checking(guess_coord):
    global num_ships
    global game_grid
    if hit_check(guess_coord, True) == True:
        # hitting an already struck ship coord
        if game_grid[guess_coord[1]][guess_coord[0]] == "X":
            outcome = -1
            return outcome
        # hitting a new ship coord
        game_grid[guess_coord[1]][guess_coord[0]] = "X"
        for x in xrange(0, len(ships)):
            if ships[x]["length"] == 0:
                num_ships -= 1
                outcome = -2
                ships[x]["length"] -= 1
                return outcome
        outcome = 0
        return outcome
    # targeting an already missed coord
    elif game_grid[guess_coord[1]][guess_coord[0]] == "-":
        outcome = -1
        return outcome
    # targeting a new coordinate and you miss!
    else:
        game_grid[guess_coord[1]][guess_coord[0]] = "-"
        outcome = 1
        return outcome

def ship_hitting():
    global board_size
    global game_grid
    mess_up_counter = 0
    guess = None
    guess_coord = None
    outcome = None
    while 1:
        guess = raw_input("Enter an attack: ")
        if coord_check(guess) == False:
            if mess_up_counter > 0:
                if randint(0, 1) == 0:
                    text_typer("Princess", "sad", 200, "I thought you said you knew how to play!", 0.05, 0, True)
                    time.sleep(0.5)
                else:
                    text_typer("Kathy", "areyoukidding", 160, "So you dont know how to play battleship...", 0.06, 0, True)
                    time.sleep(0.5)
            clear_screen()
            show_grid(game_grid)
            mess_up_counter += 1
            print "Please enter a valid attack.\n"
            continue
        break
    guess_coord = [(letters.find(guess[0]) + 1), int(guess[1])]
    outcome = hit_checking(guess_coord)
    clear_screen()
    show_grid(game_grid)
    print outcome_text[outcome]
    return outcome

def intro_dialogue():
    clear_screen()
    text_typer("Princess", "yell", 250, "WELCOME TO BATTLESHIP!", 0.06, 0, True)
    text_typer("Kathy", "talk", 150, "We are like... ", 0.09, 0, True)
    text_typer("Kathy", None, 180, "so glad to have you here. ", 0.07, 1, False)
    text_typer("Kathy", "loud", 180, "You can call me Pon.", 0.065, 0, True)
    text_typer("Princess", "talk", 190, "And my name is Tee!", 0.065, 0.01, True)
    pause_text()
    clear_screen()
    text_typer("Princess", "talk", 220, "Alrighty! ", 0.08, 0, True)
    text_typer("Princess", None, 230, "Do you know how to play?", 0.05, 0.02, False)
    text_typer("Kathy", "otalk", 160, "Oh my god, ", 0.075, 0.05, True)
    text_typer("Kathy", None, 190, "who doesn\\\'t know how to play battleship.", 0.055, 0.02, False)
    text_typer("Princess", "sad", 240, "Pon! ", 0.06, 0, True)
    text_typer("Princess", None, 200, "You cant just assume everyone ", 0.06, 0.3, False)
    text_typer("Princess", None, 130, "KNOWS ", 0.09, 0.01, False)
    text_typer("Princess", None, 220, "how to play battleship.", 0.06, 0.04, False)
    text_typer("Kathy", "loud", 120, "I can, and I will.", 0.09, 0.3, True)
    text_typer("Princess", "dotdotdot", 100, "...", 0.3, 0.3, True)
    text_typer("Princess", "talk", 210, "Please dont mind Pon. ", 0.07, 0, True)
    text_typer("Princess", None, 210, "They can be grumpy sometimes.", 0.055, 0.04, False)
    pause_text()
    clear_screen()

def main_dialogue():
    global talk_counter
    global help_counter
    global about_counter
    global games_beat
    while 1:
        sys.stdout.flush()
        clear_screen()
        if games_beat > 0:
            if randint(0, 1) == 1:
                text_typer("Princess", "talk", 210, "Ready to play?", 0.06, 0, True)
            else:
                text_typer("Kathy", "talk", 180, "Ready to play?", 0.065, 0, True)
        else:
            if randint(0, 1) == 1:
                if help_counter > 0:
                    text_typer("Princess", "talk", 210, "Did that help at all?", 0.06, 0, True)
                else:
                    text_typer("Princess", "talk", 210, "What is up!", 0.07, 0, True)
            else:
                if help_counter > 0:
                    text_typer("Kathy", "talk", 170, "Did that clarify for you?", 0.07, 0, True)
                else:
                    text_typer("Kathy", "talk", 170, "So, ", 0.08, 0, True)
                    text_typer("Kathy", None, 180, "what do you wanna do?", 0.06, 0.3, False)
        choice = raw_input("\n\nTopics: help, about, play\n> ")
        if choice == "help":
            if help_counter > 0:
                if help_counter > 1:
                    if help_counter > 2:
                        help_text()
                        help_counter += 1
                    else:
                        help_dialogue_final()
                        talk_counter += 1
                        help_counter += 1
                else:
                    help_dialogue_after()
                    talk_counter += 1
                    help_counter += 1
            else:
                help_dialogue_initial()
                talk_counter += 1
                help_counter += 1
        elif choice == "about":
            if about_counter < 1:
                about_dialogue_initial()
                about_dialogue_tree()
                about_counter += 1
                talk_counter += 1
            else:
                about_dialogue_tree()
                about_counter += 1
                talk_counter += 1
        elif choice == "play":
            clear_screen()
            if help_counter == 0:
                text_typer("Kathy", "otalk", 170, "See, ", 0.08, 0, True)
                text_typer("Kathy", None, 190, "I told you they did not need any help.", 0.06, 0.2, False)
                return True
            else:
                if talk_counter >= 4:
                    text_typer("Princess", "talk", 220, "Enough chit chat, its battleship time!", 0.065, 0, True)
                    return True
                text_typer("Kathy", "talk", 180, "Ready to play?", 0.08, 0, True)
                return True
        else:
            error_message()


def help_dialogue_initial():
    clear_screen()
    text_typer("Princess", "gasp", 210, "Oh!", 0.07, 0, True)
    text_typer("Princess", "talk", 210, "It is perfectly normal to not have played battleship before.", 0.05, 0.5, True)
    text_typer("Princess", "talk", 190, "I remember my first battleship game...", 0.06, 0, True)
    text_typer("Princess", None, 150, " just like it was yester-", 0.048, 0, False)
    text_typer("Kathy", "loud", 170, "Thats because it WAS yesterday.", 0.06, 0, True)
    text_typer("Princess", "sad", 200, "Pon!", 0.06, 0.2, True)
    text_typer("Princess", "tinysmile", 210, "Youre absolutely right!", 0.07, 1, True)
    text_typer("Princess", "talk", 190, "That is why its so fresh in my mind.", 0.055, 0, True)
    pause_text()
    clear_screen()
    text_typer("Kathy", "talk", 160, "So basically there is a grid.", 0.06, 0, True)
    text_typer("Princess", "talk", 200, "Yes a grid mmm.", 0.06, 0, True)
    text_typer("Kathy", "talk", 170, "And youre gonna guess where our ships are.", 0.052, 0, True)
    text_typer("Princess", "yell", 210, "Just try us!", 0.06, 0, True)
    text_typer("Kathy", "talk", 160, "...yeah and if you miss, ", 0.06, 0.7, True)
    text_typer("Kathy", None, 170, "youll see a little dash on the board.", 0.06, 0, False)
    text_typer("Princess", "oh", 210, "But if you hit...", 0.06, 0, True)
    text_typer("Kathy", "loud", 160, "theres gonna be a big X on the battlefield!", 0.06, 0, True)
    time.sleep(0.7)
    clear_screen()
    text_typer("Princess", "sad", 250, "Wait! ", 0.04, 0, True)
    text_typer("Princess", None, 250, "Which one is the grid and what is the battlefield?", 0.04, 0.3, False)
    text_typer("Kathy", "otalk", 170, "Oh.", 0.1, 0.5, True)
    text_typer("Kathy", "neutral", 170, "Umm...", 0.1, 0.1, True)
    text_typer("Kathy", "talk", 170, "Theyre the same thing.", 0.055, 0.1, True)
    text_typer("Princess", "oh", 200, "Well what about the board?", 0.05, 0, True)
    text_typer("Kathy", "talk", 170, "Also the same.", 0.06, 0, True)
    sys.stdout.write("\n\n" + tee["smile"] + " ")
    sys.stdout.flush()
    time.sleep(0.4)
    text_typer("Princess", "talk", 200, "Im not sure I follow but okay!", 0.06, 0.8, True)
    pause_text()
    clear_screen()
    text_typer("Kathy", "talk", 160, "Anyways, ", 0.11, 0, True)
    text_typer("Kathy", None, 170, "each ship has 2 to 4 hits it can take.", 0.06, 0.15, False)
    text_typer("Princess", "talk", 200, "So if you make a hit, ", 0.055, 0.2, True)
    text_typer("Princess", None, 220, "the rest of the ship is nearby!", 0.05, 0, False)
    text_typer("Kathy", "otalk", 170, "We\\\'ll definitely let you know if one of our ships got sunk.", 0.05, 0.2, True)
    text_typer("Princess", "oh", 200, "That is...", 0.08, 0.2, True)
    text_typer("Princess", "yell", 230, "IF YOU CAN SINK OUR SHIPS!", 0.05, 0.2, True)
    pause_text()
    clear_screen()
    text_typer("Kathy", "otalk", 165, "All of your guesses should be a letter then a number.", 0.05, 0, True)
    text_typer("Kathy", "talk", 160, "Like A1 ", 0.065, 0, True)
    text_typer("Kathy", None, 170, "or something.", 0.06, 1, False)
    text_typer("Princess", "talk", 180, "or B3!", 0.085, 0.3, True)
    text_typer("Kathy", "talk", 150, "You get the idea.", 0.075, 0.13, True)
    pause_text()

def help_dialogue_after():
    clear_screen()
    text_typer("Princess", "gasp", 210, "Oh!", 0.07, 0, True)
    text_typer("Princess", "talk", 200, "Do you need a quick recap?", 0.06, 0.5, True)
    text_typer("Kathy", "talk", 165, "Okay so its like A1 or B3.", 0.08, 0, True)
    text_typer("Kathy", "talk", 150, "And if it hits... ", 0.06, 0.6, True)
    text_typer("Kathy", "talk", 130, "youll... ", 0.07, 0.6, False)
    text_typer("Kathy", "talk", 130, "know.", 0.07, 1, False)
    text_typer("Kathy", "loud", 165, "Like it will be apparent whether or not you hit.", 0.06, 0.9, True)
    text_typer("Kathy", "talk", 165, "We\\\'ll probably even tell you.", 0.065, 0.2, True)
    text_typer("Princess", "talk", 200, "How nice of us!", 0.07, 0.1, True)
    pause_text()

def help_dialogue_final():
    clear_screen()
    text_typer("Kathy", "talk", 150, "Listen... ", 0.08, 0, True)
    text_typer("Kathy", None, 165, "Im not sure if this game is right for you.", 0.06, 0.5, False)
    sys.stdout.write("\n\n" + tee["gasp"] + " ")
    sys.stdout.flush()
    time.sleep(0.7)
    text_typer("Kathy", "loud", 150, "I mean like, ", 0.075, 0, True)
    text_typer("Kathy", None, 165, "you should follow your heart ", 0.06, 0.5, False)
    text_typer("Kathy", None, 165, "I think.", 0.06, 0.4, False)
    text_typer("Kathy", "talk", 165, "Its just concerning if you have this much trouble", 0.055, 0.4, True)
    text_typer("Kathy", "talk", 150, "with something like battleship.", 0.065, 0, True)
    text_typer("Princess", "wah", 190, "We believe in you though!", 0.057, 0.1, True)
    pause_text()

def help_text():
    clear_screen()
    print "\nThe grid is a %d by %d grid at the moment." % (board_size, board_size)
    print "\nWhen prompted, enter an attack coordinate such as E2 or C5."
    print "\nThe board will change according to whether or not you hit or miss."
    print "\nShips are generated between 2 and 4 in length."
    print "\nYou must guess that many times to actually sink the ship."
    print "\nShips can generate vertically or horizontally, so keep this in mind.\n"
    print "\nMore game modes can be unlocked after doing well on the initial game mode."
    print "\nIf you wish to leave the game, press CTRL + C."
    pause_text()

def about_dialogue_initial():
    clear_screen()
    if randint(0, 1) == 1:
        text_typer("Princess", "gasp", 210, "Oh!", 0.075, 0, True)
        text_typer("Princess", "talk", 210, "You want to know about us?", 0.055, 1, True)
    else:
        text_typer("Kathy", "otalk", 180, "Oh!", 0.075, 0, True)
        text_typer("Kathy", "talk", 180, "You want to know about us?", 0.06, 1, True)
    text_typer("Kathy", "talk", 170, "This is only moderately strange.", 0.065, 0.2, True)
    text_typer("Princess", "oh", 200, "Well, ", 0.06, 0.2, True)
    text_typer("Princess", None, 220, "what would you like to know?", 0.055, 0.5, False)
    pause_text()
    clear_screen()
    text_typer("Princess", "sad", 200, "Wait!", 0.07, 0, True)
    text_typer("Princess", "talk", 210, "If youre going to ask about my recipe", 0.055, 0.9, True)
    text_typer("Princess", "talk", 210, "for my world class carrot and cream muffins", 0.055, 0.4, True)
    text_typer("Princess", "yell", 210, "Im never going to tell yoooou!", 0.055, 0.1, True)
    text_typer("Kathy", "talk", 180, "Tee, ", 0.065, 0.3, True)
    text_typer("Kathy", "talk", 160, "Im going to take a wild guess", 0.065, 0.3, True)
    text_typer("Kathy", "talk", 180, "and say that is not what they were going to ask.", 0.052, 0.05, True)
    text_typer("Princess", "dotdotdot", 60, "Mmm...", 0.08, 0.5, True)
    text_typer("Princess", "talk", 160, "I wouldn\\\'t be so sure if I were you!", 0.06, 0.65, True)
    pause_text()

def about_dialogue_tree():
    global about_topics
    global about_counter
    global talk_counter
    global pon_counter
    global tee_counter
    global food_counter
    global error_message
    global pon_ready
    global tee_ready
    decisions = None
    while 1:
        topics = "\n\nTopics: nothing"
        for x in xrange(len(about_topics)):
            topics += ", %s" % about_topics[x]
        topics += "\n> "
        clear_screen()
        if randint(0, 1) == 1:
            text_typer("Princess", "oh", 100, "So, ", 0.09, 0.1, True)
            text_typer("Princess", None, 210, "what did you want to ask about?", 0.055, 0.4, False)
        else:
            text_typer("Kathy", "talk", 180, "What do you wanna know.", 0.058, 0.1, True)
        about_choice = raw_input(topics)
        for x in xrange(len(about_topics)):
            if about_choice == about_topics[x] or about_choice == "nothing":
                if about_choice == "nothing":
                    if randint(0, 1) == 1:
                        text_typer("Princess", "talk", 210, "Perhaps we can talk again another time.", 0.055, 0.1, True)
                        pause_text()
                        return True
                    else:
                        text_typer("Kathy", "talk", 175, "You can always talk to us at a later time.", 0.06, 0.1, True)
                        pause_text()
                        return True
                elif about_choice == "color":
                    about_dialogue_color()
                    about_topics.remove("color")
                    break
                elif about_choice == "music":
                    about_dialogue_music()
                    about_topics.remove("music")
                    if pon_counter > 2 and pon_ready == False:
                        pon_ready = True
                        about_topics.append("Pon")
                    break
                elif about_choice == "muffins":
                    about_dialogue_muffins()
                    about_topics.remove("muffins")
                    about_topics.append("food")
                    if tee_counter > 1 and tee_ready == False:
                        tee_ready = True
                        about_topics.append("Tee")
                    break
                elif about_choice == "games":
                    about_dialogue_games()
                    about_topics.remove("games")
                    if tee_counter > 1 and tee_ready == False:
                        tee_ready = True
                        about_topics.append("Tee")
                    if pon_counter > 2 and pon_ready == False:
                        pon_ready = True
                        about_topics.append("Pon")
                    break
                elif about_choice == "food":
                    if about_dialogue_food() == False:
                        pass
                    else:
                        food_counter += 1
                    if food_counter > 2:
                        about_topics.remove("food")
                    if pon_counter > 2 and pon_ready == False:
                        pon_ready = True
                        about_topics.append("Pon")
                    break
                elif about_choice == "Tee":
                    about_dialogue_tee()
                    about_topics.remove("Tee")
                    break
                elif about_choice == "Pon":
                    about_dialogue_pon()
                    about_topics.remove("Pon")
                    break
                elif about_choice == "Jeremy":
                    about_dialogue_jeremy()
                    about_topics.remove("Jeremy")
                    break
                else:
                    error_message()
                    talk_counter -= 1
        talk_counter += 1

def about_dialogue_color():
    global decisions
    color_talk = ""
    clear_screen()
    text_typer("Princess", "wah", 180, "Lets see...", 0.075, 0.1, True)
    text_typer("Princess", None, 160, " my favorite color is... ", 0.075, 0.2, False)
    text_typer("Princess", "talk", 210, "Blue!", 0.075, 0.7, True)
    text_typer("Princess", "oh", 220, "But not just any bloo.", 0.06, 0.5, True)
    text_typer("Princess", "talk", 200, "Sky blu!", 0.07, 0.7, True)
    text_typer("Princess", "talk", 220, "Whats your favorite color, friend?", 0.06, 0.7, True)
    decisions = raw_input("\n\n> ")
    if len(decisions) > 10:
        color_talk = "My grandma used to paint her fence that color "
    else:
        color_talk = "My grandma used to paint her fence bright %s " % decisions
    clear_screen()
    text_typer("Princess", "talk", 200, "Oh what a good color!", 0.06, 0.2, True)
    text_typer("Princess", "talk", 215, color_talk, 0.055, 0.4, True)
    text_typer("Princess", None, 200, "almost every year.", 0.06, 0.4, False)
    text_typer("Princess", "oh", 180, "What about you Pon, ", 0.065, 0.4, True)
    text_typer("Princess", None, 200, "whats your favorite color?", 0.06, 0.3, False)
    text_typer("Kathy", "otalk", 150, "Its-", 0.05, 0.15, True)
    text_typer("Princess", "sad", 200, "Wait!", 0.07, 0, True)
    sys.stdout.write("\n\n" + pon["neutral"] + " ")
    sys.stdout.flush()
    time.sleep(0.65)
    text_typer("Princess", "wah", 210, "Its purple, ", 0.06, 0.1, True)
    text_typer("Princess", None, 210, "isnt it?", 0.06, 0.3, False)
    text_typer("Kathy", "talk", 180, "So close, ", 0.07, 0.1, True)
    text_typer("Kathy", "talk", 180, "but its #CCCCFF.", 0.067, 0.4, False)
    text_typer("Princess", "gasp", 180, "Wow.", 0.1, 0.8, True)
    pause_text()
    clear_screen()


def about_dialogue_music():
    global decisions
    global pon_counter
    clear_screen()
    text_typer("Kathy", "talk", 180, "My fav band is Crushing Moldlick. ", 0.06, 0.1, True)
    text_typer("Kathy", None, 180, "Youve probably never heard of them.", 0.06, 0.6, False)
    decisions = raw_input("\n\nyes/no > ")
    if decisions == "yes":
        text_typer("Kathy", "on_to_you", 100, "Hmm...", 0.08, 0.2, True)
        text_typer("Kathy", "talk", 180, "Whats your favorite song by them?", 0.06, 0.5, True)
        decisions = raw_input("\n\n> ")
        text_typer("Kathy", "areyoukidding", 180, "I lied to you.", 0.07, 0, True)
        text_typer("Kathy", "talk", 180, "Theyre not a real band, ", 0.07, 0.1, True)
        text_typer("Kathy", None, 180, "I was just testing you.", 0.07, 0.4, False)
    else:
        text_typer("Kathy", "loud", 180, "I knew it.", 0.06, 0.1, True)
        sys.stdout.write("\n\n" + pon["neutral"] + " ")
        sys.stdout.flush()
        time.sleep(1)
        text_typer("Kathy", "unsure", 180, "Sorry, ", 0.07, 0.4, True)
        text_typer("Kathy", None, 180, "I lied to you...", 0.07, 0.8, False)
        text_typer("Kathy", "talk", 180, "My favorite band is actually ", 0.06, 0.1, True)
        text_typer("Kathy", None, 240, "Red Hot Chili Peppers.", 0.05, 0.8, False)
        pon_counter += 1
    pause_text()
    clear_screen()
    text_typer("Kathy", "talk", 180, "Tee, ", 0.08, 0.1, True)
    text_typer("Kathy", "talk", 180, "what about you?", 0.065, 0.3, False)
    text_typer("Princess", "talk", 210, "I thought you\\\'d never ask!", 0.055, 0.1, True)
    text_typer("Princess", "talk", 210, "My favorite kind of music kinda sounds like...", 0.055, 0.1, True)
    text_typer("Princess", "talk", 200, "Kinda like: ", 0.07, 0.5, True)
    subprocess.Popen('say -v Deranged -r 120 "La la la!"', shell=True)
    text_typer(None, None, None, "La la la! ", 0.1, 0.2, False)
    text_typer("Princess", "talk", 210, "You know what I mean?", 0.06, 0.6, True)
    text_typer("Kathy", "talk", 120, "Kinda.", 0.1, 0.6, True)
    pause_text()
    clear_screen()


def about_dialogue_muffins():
    global tee_counter
    clear_screen()
    text_typer("Princess", "yell", 230, "I knew it!", 0.075, 0.1, True)
    text_typer("Kathy", "neutral", 210, "...", 0.2, 0.2, True)
    text_typer("Princess", "wah", 220, "Ive known since the minute you walked in ", 0.055, 0.7, True)
    text_typer("Princess", None, 180, "that you are...", 0.07, 0.1, False)
    text_typer("Princess", "oh", 120, "A muffin lover.", 0.08, 1, True)
    text_typer("Kathy", "talk", 210, "...Im going to the bathroom brb.", 0.065, 0.3, True)
    text_typer("Princess", "talk", 180, "Dont worry, ", 0.08, 0, True)
    text_typer("Princess", None, 210, "your secret is safe with me!", 0.055, 0.2, False)
    pause_text()
    clear_screen()
    text_typer("Princess", "wah", 200, "As I was saying...", 0.075, 0, True)
    text_typer("Princess", "talk", 200, "My carrot n cream muffins are the best muffins there is.", 0.055, 0.2, True)
    text_typer("Princess", "talk", 190, "Every year at the bakery olympics Pon and I enter", 0.061, 0.2, True)
    text_typer("Princess", "talk", 210, "I submit my muffins to the competition and Pon-", 0.050, 0, True)
    text_typer("Kathy", "talk", 180, "I am back.", 0.07, 0, True)
    text_typer("Kathy", "talk", 180, "You were talking about me weren\\\'t you.", 0.0535, 0.3, True)
    text_typer("Princess", "oh", 160, "Oh!", 0.09, 0.09, True)
    text_typer("Princess", "talk", 200, "I was just about to say that you make the best boysenberry tarts!", 0.05, 0.5, True)
    text_typer("Kathy", "talk", 180, "Why thank you.", 0.07, 0.4, True)
    tee_counter += 1
    pause_text()
    clear_screen()

def about_dialogue_games():
    global decisions
    global tee_counter
    global pon_counter
    clear_screen()
    text_typer("Kathy", "otalk", 160, "Omg I LOVE games. ", 0.08, 0, True)
    text_typer("Kathy", None, 180, "Video games especially so.", 0.07, 0.6, False)
    text_typer("Princess", "talk", 180, "Personally, ", 0.075, 0.1, True)
    text_typer("Princess", None, 210, "Im a board games kind of gal.", 0.062, 0.25, False)
    text_typer("Princess", "oh", 180, "Ever play Settlers of Catan?", 0.07, 0.2, True)
    decisions = raw_input("\n\nyes/no > ")
    clear_screen()
    if decisions == "yes":
        text_typer("Princess", "gasp", 180, "Oh!", 0.07, 0.2, True)
        text_typer("Princess", "talk", 210, "Finally someone who plays it!", 0.06, 0.4, True)
        text_typer("Kathy", "loud", 180, "Now she can stop bugging me to play with her.", 0.06, 0.15, True)
        text_typer("Princess", "talk", 180, "Oh Pon, ", 0.07, 0.1, True)
        text_typer("Princess", None, 200, "you are too funny!", 0.065, 0.3, False)
        tee_counter += 1
    else:
        text_typer("Princess", "sad", 210, "You\\\'re really missing out!", 0.055, 0.2, True)
        text_typer("Princess", "oh", 210, "Ive been trying to get Pon to play it", 0.06, 0.1, True)
        text_typer("Princess", "oh", 210, "for who knows how long.", 0.06, 0, True)
        text_typer("Kathy", "loud", 180, "At least 20 years.", 0.11, 0.4, True)
    pause_text()
    clear_screen()
    text_typer("Kathy", "talk", 160, "As for me, ", 0.075, 0.1, True)
    text_typer("Kathy", None, 180, "my fav video game is Shingen The Ruler.", 0.065, 0.25, False)
    text_typer("Kathy", "talk", 200, "The strategy, ", 0.075, 0.1, True)
    text_typer("Kathy", None, 130, "the pain. ", 0.075, 0.2, False)
    text_typer("Kathy", "neutral", 160, "The decisions you make... ", 0.075, 0.5, True)
    text_typer("Kathy", "talk", 180, "What a refreshing game.", 0.065, 0.7, True)
    decisions = raw_input("\n\nI agree / You're weird > ")
    if decisions == "I agree":
        text_typer("Kathy", "talk", 180, "Im glad you understand.", 0.07, 0.1, True)
        pon_counter += 1
    elif decisions == "You're weird":
        text_typer("Kathy", "loud", 190, "You just dont understand me, ", 0.06, 0.1, True)
        text_typer("Kathy", None, 180, "do you.", 0.07, 0.2, False)
    else:
        text_typer("Kathy", "neutral", 140, "...right.", 0.075, 0.5, True)
    pause_text()
    clear_screen()

def about_dialogue_food():
    global decisions
    global tee_counter
    global pon_counter
    global food_counter
    ask_about = "\n\nAsk about: nevermind"
    for x in xrange(len(food_topics)):
        ask_about += ", %s" % food_topics[x]
    ask_about += "\n> "
    clear_screen()
    if food_counter == 0:
        text_typer("Kathy", "talk", 180, "Aside from baking, ", 0.07, 0.1, True)
        text_typer("Kathy", None, 180, "Im not much of a cook.", 0.065, 0.3, False)
        text_typer("Princess", "talk", 150, "Me either!", 0.08, 0.1, True)
        text_typer("Princess", "oh", 190, "Maybe we could learn together!", 0.06, 0.2, True)
    decisions = raw_input(ask_about)
    clear_screen()
    if decisions == "favfood" and ask_about.find(decisions) != -1:
        text_typer("Kathy", "talk", 180, "Honestly, ", 0.065, 0, True)
        text_typer("Kathy", None, 180, "anything with barbecue sauce I will eat.", 0.06, 0.4, False)
        text_typer("Princess", "oh", 210, "If I put some on a cauliflower, ", 0.06, 0.1, True)
        text_typer("Princess", None, 210, "would you eat it?", 0.062, 0.4, False)
        text_typer("Kathy", "loud", 180, "Definitely.", 0.062, 0.1, True)
        text_typer("Kathy", "talk", 195, "My love of bbq sauce trumps my hatred of cauliflower.", 0.065, 0.2, True)
        text_typer("Princess", "talk", 210, "If there was a deluxe bbq burger from BurgWorld on the ground with", 0.053, 0, True)
        text_typer("Princess", "dotdotdot", 100, "mold on it", 0.083, 0.4, True)
        text_typer("Princess", "oh", 200, "would you eat that?", 0.057, 0.2, True)
        text_typer("Kathy", "neutral", 190, "Anything for the B-B-Q.", 0.065, 0.5, True)
        text_typer("Princess", "gasp", 180, "Inspiring.", 0.07, 0.9, True)
        if tee_counter > 1:
            pause_text()
            clear_screen()
            text_typer("Princess", "oh", 200, "Im not supposed to talk about it but,", 0.055, 0.1, True)
            sys.stdout.write("\n\n" + tee["dotdotdot"] + " ")
            sys.stdout.flush()
            time.sleep(1)
            text_typer("Princess", "gasp", 180, "I love avocado.", 0.068, 0, True)
            time.sleep(0.5)
            sys.stdout.write("\n\n" + pon["areyoukidding"] + " ")
            sys.stdout.flush()
            time.sleep(1.5)
            food_topics.append("avocado")
    elif decisions == "muffins" and ask_about.find(decisions) != -1:
        text_typer("Princess", "sad", 210, "You\\\'re insatiable, ", 0.06, 0.1, True)
        text_typer("Princess", None, 210, "arent you!", 0.065, 0.18, False)
        text_typer("Princess", "talk", 210, "I am glad that you are unashamed in your passion.", 0.055, 0.2, True)
        text_typer("Kathy", "talk", 180, "Muffin lovers are definitely a minority, ", 0.06, 0.1, True)
        text_typer("Kathy", None, 150, "Tee.", 0.095, 0.2, False)
        text_typer("Princess", "yell", 250, "Shut up!", 0.048, 0.05, True)
        time.sleep(0.5)
        sys.stdout.write("\n\n" + pon["smiley"] + " ")
        sys.stdout.flush()
        time.sleep(1)
        pon_counter += 1
    elif decisions == "lunch" and ask_about.find(decisions) != -1:
        text_typer("Princess", "yell", 220, "LUNCH TIME IS THE BEST TIME!", 0.055, 0.1, True)
        sys.stdout.write("\n\n" + tee["smile"] + " ")
        sys.stdout.flush()
        time.sleep(1.5)
        sys.stdout.write("\n\n" + pon["neutral"] + " ")
        sys.stdout.flush()
        time.sleep(1.5)
        sys.stdout.write("\n\n" + tee["talk"] + " ")
        sys.stdout.flush()
        time.sleep(1.5)
        sys.stdout.write("\n\n" + pon["areyoukidding"] + " ")
        sys.stdout.flush()
        time.sleep(1.5)
        text_typer("Kathy", "loud", 195, "Weve talked about this before and dinner time is clearly the superior-", 0.045, 0, True)
        text_typer("Princess", "talk", 140, "Its lunch time!", 0.06, 0, True)
    elif decisions == "avocado" and ask_about.find(decisions) != -1:
        text_typer("Kathy", "talk", 180, "We do not talk about avocados around here.", 0.06, 0.1, True)
        text_typer("Princess", "sad", 190, "Pon! ", 0.07, 0.4, True)
        text_typer("Princess", None, 210, "We can talk about the incident if you like.", 0.055, 0.3, False)
        sys.stdout.write("\n\n" + pon["neutral"] + " ")
        sys.stdout.flush()
        time.sleep(3)
        text_typer("Kathy", None, 140, "Fine.", 0.1, 0, False)
        text_typer("Kathy", "otalk", 180, "Basically everything is Jeremys fault.", 0.06, 0.3, True)
        pause_text()
        clear_screen()
        text_typer("Kathy", "talk", 180, "There was this party that I was invited to by Jeremy.", 0.055, 0.1, True)
        text_typer("Kathy", "loud", 180, "And he told me that it was a fruit costume party.", 0.055, 0.1, True)
        text_typer("Kathy", "talk", 180, "So I was like ", 0.055, 0.2, True)
        text_typer("Kathy", None, 60, "okay ", 0.2, 0.35, False)
        text_typer("Kathy", "talk", 180, "and bought this weird avocado suit from this guy in the alley.", 0.0535, 0.1, True)
        text_typer("Kathy", "unsure", 180, "And I showed to the party with this suit on and everyone was...", 0.055, 0.2, True)
        text_typer("Kathy", "otalk", 150, "dressed as dairy products!", 0.065, 0.4, True)
        test = raw_input("\n\nReply: omg jerk / lol\n> ")
        clear_screen()
        if test == "omg jerk":
            text_typer("Kathy", "talk", 180, "Right?", 0.07, 0.1, True)
            pon_counter += 1
        elif test == "lol":
            sys.stdout.write("\n\n" + pon["areyoukidding"] + " ")
            sys.stdout.flush()
            time.sleep(0.8)
            text_typer("Princess", "sad", 180, "Uh oh!", 0.07, 0, True)
            text_typer("Kathy", "talk", 180, "Tee, ", 0.07, 0.1, True)
            text_typer("Kathy", "talk", 160, "we are leaving this jerk.", 0.065, 0.3, True)
            text_typer("Princess", "sad", 180, "Pon!", 0.07, 0, True)
            clear_screen()
            text_typer(None, None, None, "\n\nYou jerk.", 0.15, 0, False)
            sys.exit()
        else:
            text_typer("Kathy", "neutral", 180, "...yeah.", 0.07, 0.2, True)
        text_typer("Kathy", "talk", 180, "He is the worst. ", 0.07, 0.2, True)
        text_typer("Kathy", None, 100, "Ugh.", 0.1, 0.4, False)
        time.sleep(0.5)
    else:
        text_typer("Princess", "talk", 190, "You can ask about that later.", 0.06, 0, True)
        pause_text()
        return False
    food_topics.remove(decisions)
    pause_text()

def about_dialogue_tee():
    clear_screen()
    text_typer("Princess", "oh", 200, "There isnt much to know about lil ol me.", 0.055, 0, True)
    text_typer("Princess", "talk", 205, "But thank you for asking!", 0.055, 0.2, True)
    text_typer("Kathy", "talk", 180, "I can speak on your behalf.", 0.06, 0.2, True)
    text_typer("Princess", "sad", 180, "Pon!", 0.075, 0, True)
    text_typer("Kathy", "talk", 180, "Tee is a total weirdo.", 0.06, 0.2, True)
    text_typer("Princess", "sad", 180, "Oh my god!", 0.07, 0, True)
    text_typer("Kathy", "talk", 180, "But ", 0.08, 0.2, True)
    text_typer("Kathy", None, 180, "like, ", 0.08, 0.25, False)
    text_typer("Kathy", None, 180, "in a great way.", 0.06, 0.4, False)
    pause_text()
    clear_screen()
    text_typer("Princess", "sad", 210, "Why do you have to be so embarassing!", 0.055, 0.1, True)
    text_typer("Kathy", "smiley", 180, "Heh, ", 0.08, 0.4, True)
    text_typer("Kathy", None, 180, "okay I\\\'ll stop.", 0.06, 0.2, False)
    text_typer("Princess", "wah", 200, "Thank you.", 0.06, 0.3, True)
    sys.stdout.write("\n\n" + pon["neutral"] + " ")
    sys.stdout.flush()
    time.sleep(2)
    text_typer("Kathy", None, 220, "Tee also really enjoys picking scabs-", 0.0535, 0, False)
    text_typer("Kathy", "loud", 240, "Not only on her but on other people too!", 0.05, 0.1, True)
    text_typer("Princess", "sad", 210, "I cannot believe this!", 0.055, 0, True)
    pause_text()
    clear_screen()
    text_typer("Kathy", "talk", 190, "No but for real, ", 0.06, 0.1, True)
    text_typer("Kathy", None, 180, "dont ever change, ", 0.06, 0.2, False)
    text_typer("Kathy", None, 180, "Tee.", 0.06, 0.2, False)
    sys.stdout.write("\n\n" + tee["oh"] + " ")
    sys.stdout.flush()
    time.sleep(1)
    text_typer("Kathy", "talk", 180, "I wouldn\\\'t want you any other way!", 0.0575, 0, True)
    text_typer("Princess", "talk", 120, "Aww!", 0.085, 0.2, True)
    text_typer("Princess", "smile", 200, "Thank you, ", 0.07, 0.4, True)
    text_typer("Princess", None, 200, "Pon!", 0.07, 0.1, False)
    text_typer("Kathy", "talk", 180, "No problem.", 0.07, 0.2, True)
    pause_text()

def about_dialogue_pon():
    global decisions
    global about_topics
    global pon_counter
    clear_screen()
    text_typer("Kathy", "talk", 180, "Thats me. ", 0.07, 0.1, True)
    text_typer("Kathy", None, 180, "Pon de la Mon.", 0.06, 0.2, False)
    text_typer("Princess", "oh", 180, "Wait, ", 0.085, 0.2, True)
    text_typer("Princess", False, 210, "is that actually your full name?!", 0.055, 0.3, False)
    text_typer("Kathy", "talk", 180, "No ", 0.07, 0.2, True)
    text_typer("Kathy", None, 180, "lol.", 0.07, 0.2, False)
    text_typer("Princess", "talk", 200, "You trickster, ", 0.07, 0.3, True)
    text_typer("Princess", False, 180, "you!", 0.08, 0, False)
    text_typer("Kathy", "talk", 180, "Im not quite sure what you want to know.", 0.0575, 0.1, True)
    decisions = raw_input("\n\nAsk about: Jeremy / free time\n> ")
    clear_screen()
    if decisions == "Jeremy" or decisions == "jeremy":
        if pon_counter > 3:
            sys.stdout.write("\n\n" + pon["neutral"] + " ")
            sys.stdout.flush()
            time.sleep(1)
            text_typer("Kathy", None, 180, "We can talk more about that later.", 0.06, 0, False)
            about_topics.append("Jeremy")
        else:
            text_typer("Kathy", "talk", 180, "Dont worry, ", 0.06, 0, True)
            text_typer("Kathy", None, 180, "Im over it.", 0.06, 0.3, False)
            text_typer("Kathy", "talk", 180, "Just dont ever trust a Jeremy.", 0.0575, 0.1, True)
    elif decisions == "free time":
        text_typer("Kathy", "unsure", 150, "What free time?", 0.07, 0, True)
        text_typer("Kathy", "talk", 180, "We sit and wait for the next person to come along.", 0.055, 0.2, True)
        text_typer("Kathy", "loud", 200, "We\\\'ve been playing this game for as long as I can remember.", 0.055, 0.3, True)
        text_typer("Princess", "sad", 200, "Forgive us for the limited information we have.", 0.06, 0.1, True)
        text_typer("Kathy", "neutral", 140, "I can barely remember who I used to be-", 0.07, 0.1, True)
        text_typer("Kathy", "talk", 180, "Sorry.", 0.07, 1, True)
        pause_text()
        clear_screen()
        text_typer("Princess", "frown", 200, "We should not dwell.", 0.06, 0, True)
        text_typer("Kathy", "neutral", 180, "You are right.", 0.0675, 0.4, True)
        text_typer("Princess", "talk", 210, "What matters is that you are here with us!", 0.0535, 0.15, True)
        text_typer("Kathy", "talk", 180, "And we are going to have a good time!", 0.06, 0.25, True)
    else:
        text_typer("Kathy", "talk", 180, "We should get back to playing battleship.", 0.0575, 0, True)
        text_typer("Princess", "talk", 200, "I agree!", 0.065, 0.2, True)
    pause_text()

def about_dialogue_jeremy():
    clear_screen()
    text_typer("Kathy", "talk", 180, "Jeremy Jeremy Jeremy.", 0.06, 0, True)
    text_typer("Kathy", "otalk", 200, "What a little freak!", 0.055, 0.5, True)
    text_typer("Princess", "oh", 200, "If I ever see him again...", 0.055, 0.2, True)
    text_typer("Princess", "yell", 230, "Im going to beat him up so bad!", 0.0535, 0.3, True)
    text_typer("Kathy", "talk", 180, "No need to, ", 0.06, 0.1, True)
    text_typer("Kathy", None, 170, "Tee.", 0.07, 0.1, False)
    text_typer("Princess", "dotdotdot", 120, "He better watch it.", 0.075, 0.4, True)
    pause_text()
    clear_screen()
    text_typer("Kathy", "neutral", 160, "So, ", 0.08, 0.1, True)
    text_typer("Kathy", None, 180, "I kinda had a crush on him. ", 0.06, 0.3, False)
    text_typer("Kathy", None, 180, "Like a lot.", 0.065, 0.5, False)
    text_typer("Princess", "yell", 180, "He doesn\\\'t deserve youuu!", 0.06, 0.2, True)
    text_typer("Kathy", "talk", 200, "Calm down.", 0.06, 0, True)
    text_typer("Kathy", "talk", 180, "Ive moved on, ", 0.06, 0.3, True)
    text_typer("Kathy", None, 180, "dont worry.", 0.06, 0.4, False)
    text_typer("Princess", "dotdotdot", 150, "I hope he becomes lactose intolerant.", 0.067, 0.4, True)
    text_typer("Kathy", "talk", 180, "Lol.", 0.1, 0.5, True)
    pause_text()

def game_end_dialogue():
    global guesses
    global decisions
    global talk_counter
    global board_size
    low_thresh_hold = Math.floor((board_size * board_size)/5)
    high_thresh_hold = Math.ceil((board_size * board_size)/3)
    talk_counter = 0
    clear_screen()
    text_typer("Princess", "talk", 190, "You won!", 0.07, 0.1, True)
    if guesses < low_thresh_hold:
        text_typer("Princess", "oh", 210, "You are a battleship master.", 0.06, 0.2, True)
        text_typer("Kathy", "talk", 180, "I underestimated you.", 0.065, 0.2, True)
    elif guesses > high_thresh_hold:
        text_typer("Princess", "oh", 210, "I think you need some more practice.", 0.057, 0.2, True)
        text_typer("Kathy", "otalk", 180, "It was fun though.", 0.065, 0.1, True)
    else:
        text_typer("Princess", "oh", 210, "I think we\\\'re about even in skill!", 0.055, 0.2, True)
        text_typer("Kathy", "talk", 180, "Dont get too cocky.", 0.065, 0.1, True)
    pause_text()
    clear_screen()
    if randint(0, 1) == 1:
        text_typer("Princess", "talk", 210, "Did you want to play again?", 0.06, 0, True)
    else:
        text_typer("Kathy", "talk", 180, "Ready for another round?", 0.065, 0, True)
    decisions = raw_input("\n\nY/N > ")
    if decisions == "Y" or decisions == "y" or decisions == "yes" or decisions == "Yes":
        text_typer("Princess", "talk", 210, "Fire up those engines, ", 0.06, 0, True)
        text_typer("Princess", None, 185, "its battleship time!", 0.07, 0.5, False)
        return True
    else:
        text_typer("Princess", "sad", 160, "Aww!", 0.09, 0, True)
        text_typer("Kathy", "talk", 180, "We will miss you.", 0.06, 0, True)
        text_typer("Princess", "talk", 190, "Come back soon!", 0.09, 0, True)
        return False

def pause_text():
    pause("\n\nPress any key to continue.")
    return None

def error_message():
    if randint(0, 1) == 0:
        text_typer("Princess", "sad", 220, error_text["tee"][randint(0, len(error_text["tee"]) - 1)], 0.06, 0, True)
        time.sleep(0.5)
    else:
        text_typer("Kathy", "unsure", 180, error_text["pon"][randint(0, len(error_text["pon"]) - 1)], 0.06, 0, True)
        time.sleep(0.5)

# initializing function to start the game, asking for input
def start_game():
    global games_beat
    global user_input
    global game_grid
    global board_size
    global num_ships
    global guesses
    global ships
    while 1:
        try:
            user_input = int(raw_input("\n> Enter board dimensions: "))
        except ValueError:
            print "> Please input a valid integer.\n"
            continue

        if user_input < 5:
            print "The battlefield will be too small! Try bigger.\n"
            continue
        elif user_input > 9:
            print "The battlefield will be too big... Try smaller.\n"
            continue

        board_size = user_input
        break
    # if games_beat == 0:
    #     intro_dialogue()
    main_dialogue()
    game_grid = []
    num_ships = board_size - 2
    game_grid = grid_setup()
    ship_generator()
    sys.stdout.write("\n\n" + tee["talk"] + " ")
    sys.stdout.write(pon["talk"] + " ")
    subprocess.Popen('say -v Princess -r 100 "Let\'s begin!"', shell=True)
    subprocess.Popen('say -v Kathy -r 100 "Let\'s begin!"', shell=True)
    text_typer(None, None, None, "Let's begin!", 0.1, 0, False)
    time.sleep(0.6)
    clear_screen()
    show_grid(game_grid)
    sys.stdout.flush()
    guesses = 0
    while 1:
        if num_ships == 0:
            break
        if ship_hitting() > 0:
            guesses += 1
    games_beat += 1
    print "End game! You missed %d times." % guesses
    pause_text()
    if game_end_dialogue() == True:
        ships = []
        clear_screen()
        start_game()
    else:
        sys.exit()


"""""""""""""""
-----START-----
-----GAME!-----
"""""""""""""""

# clear the screen before starting
clear_screen()

try:
    # let users know what's up!
    print "\nBattleship uses a square grid, please input one number for the width and height\n"

    # let's begin!
    start_game()

except KeyboardInterrupt:
    os.system('clear')
    subprocess.Popen('say -v Princess "Byeee! We\'ll see you later!"', shell=True)
    time.sleep(2.2)
    subprocess.call('say -v Kathy "Finally."', shell=True)
    sys.exit()
