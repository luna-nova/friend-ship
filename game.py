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

# let users know what's up!
print "\nBattleship uses a square grid, please input one number for the width and height\n"

# continuous loop until user inputs a valid grid size
while 1:
    try:
        user_input = int(raw_input("> Enter board dimensions: "))
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

ships = []
num_ships = board_size - 3
talk_counter = 0
help_counter = 0
about_counter = 0

icons = {
    "checkmark": u'\u2713',
    "fill_square": u'\u2588',
}

pon = {
    "neutral": u'[\u25E6_\u25E6]',
    "unsure": u'[\u25E6~\u25E6]',
    "talk": u'[\u25E6\u25B4\u25E6]',
    "otalk": u'[\u25E6o\u25E6]',
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
    "sad": u'(\u02DA\u2313 \u02DA)',
    "oh": u'(\u02DA\u25AB\u02DA)',
    "gasp": u'(\u02DA\u25C7\u02DA)',
    "dotdotdot": u'(\u02DA\u23BB\u02DA)',
}

help_text = {
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
about_topics = ["color", "music", "muffins"]


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
def grid_setup(board_size):
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
def coord_check(coord, board_size):
    match_string = re.compile("^[A-%s][1-%d]$" % (letters[board_size-1], board_size))
    if re.match(match_string, coord, flags=0):
        return True
    else:
        return False

def ship_generator(board_size):
    number_of_ships = num_ships
    alignments = ["left", "right", "up", "down"]

    while number_of_ships > 0:
        # if a generation iteration (lol) didn't work then reset variables and try again
        ship_length = randint(2, 4)
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
def hit_checking(guess_coord, game_grid):
    global num_ships
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

def ship_hitting(board_size, game_grid):
    mess_up_counter = 0
    guess = None
    guess_coord = None
    outcome = None
    while 1:
        guess = raw_input("Enter an attack: ")
        if coord_check(guess, board_size) == False:
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
    outcome = hit_checking(guess_coord, game_grid)
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
    text_typer("Princess", "dotdotdot", 100, "...", 0.3, 0, True)
    text_typer("Princess", "talk", 210, "Please dont mind Pon. ", 0.07, 0, True)
    text_typer("Princess", None, 210, "They can be grumpy sometimes.", 0.06, 0.025, False)
    pause_text()
    clear_screen()

def main_dialogue():
    global talk_counter
    global help_counter
    global about_counter
    while 1:
        sys.stdout.flush()
        clear_screen()
        if randint(0, 1) == 0:
            if help_counter > 0:
                text_typer("Princess", "talk", 210, "Did that help at all?", 0.06, 0, True)
            else:
                text_typer("Princess", "talk", 210, "What is up!", 0.07, 0, True)
        else:
            if help_counter > 0:
                text_typer("Kathy", "talk", 170, "Did that clarify for you?", 0.07, 0, True)
            else:
                text_typer("Kathy", "talk", 170, "So, ", 0.08, 0, True)
                text_typer("Kathy", None, 180, "what do you wanna do?", 0.055, 0.2, False)
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
                # about_dialogue_initial()
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
                if talk_counter >= 8:
                    text_typer("Princess", "talk", 220, "Enough chit chat, its battleship time!", 0.065, 0, True)
                    return True
                text_typer("Kathy", "talk", 180, "Ready to play?", 0.08, 0, True)
                return True
        else:
            if randint(0, 1) == 0:
                text_typer("Princess", "sad", 220, help_text["tee"][randint(0, len(help_text["tee"]) - 1)], 0.06, 0, True)
                time.sleep(0.5)
            else:
                text_typer("Kathy", "unsure", 180, help_text["pon"][randint(0, len(help_text["pon"]) - 1)], 0.06, 0, True)
                time.sleep(0.5)

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
    decisions = None
    while 1:
        topics = "\n\nTopics: nothing"
        for x in xrange(len(about_topics)):
            topics += ", %s" % about_topics[x]
        topics += "\n> "
        clear_screen()
        text_typer("Princess", "oh", 100, "So, ", 0.09, 0.1, True)
        text_typer("Princess", None, 210, "what did you want to ask about?", 0.055, 0.4, False)
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
                elif about_choice == "music":
                    about_dialogue_music()
                elif about_choice == "muffins":
                    about_dialogue_muffins()
                    about_topics.remove("muffins")
                elif about_choice == "games":
                    about_dialogue_games()
                elif about_choice == "food":
                    about_dialogue_food()
                elif about_choice == "Tee":
                    about_dialogue_tee()
                elif about_choice == "Pon":
                    about_dialogue_pon()
                elif about_choice == "Jeremy":
                    about_dialogue_jeremy()

def about_dialogue_color():
    return True

def about_dialogue_music():
    return True

def about_dialogue_muffins():
    clear_screen()
    text_typer("Princess", "yell", 240, "I knew it!", 0.075, 0.1, True)
    text_typer("Kathy", "neutral", 210, "...", 0.2, 0.2, True)
    text_typer("Princess", "wah", 220, "Ive known since the minute you walked in ", 0.056, 0.7, True)
    text_typer("Princess", None, 180, "that you are...", 0.07, 0.1, False)
    text_typer("Princess", "oh", 120, "A muffin lover.", 0.08, 1, True)
    text_typer("Kathy", "talk", 210, "...Im going to the bathroom brb.", 0.065, 0.3, True)
    text_typer("Princess", "talk", 180, "Dont worry, ", 0.08, 0, True)
    text_typer("Princess", None, 210, "your secret is safe with me!", 0.055, 0.25, False)
    pause_text()
    clear_screen()
    text_typer("Princess", "wah", 200, "As I was saying...", 0.075, 0, True)
    text_typer("Princess", "talk", 200, "My carrot n cream muffins are the best muffins there is.", 0.055, 0.3, True)
    text_typer("Princess", "talk", 190, "Every year at the bakery olympics Pon and I enter", 0.061, 0.2, True)
    text_typer("Princess", "talk", 210, "I submit my muffins to the competition and Pon-", 0.050, 0, True)
    text_typer("Kathy", "talk", 180, "I am back.", 0.07, 0, True)
    text_typer("Kathy", "talk", 180, "You were talking about me weren\\\'t you.", 0.057, 0.3, True)
    text_typer("Princess", "oh", 160, "Oh!", 0.09, 0, True)
    text_typer("Princess", "talk", 200, "I was just about to say that you make the best boysenberry tarts!", 0.053, 0.5, True)
    text_typer("Kathy", "talk", 180, "Why thank you.", 0.07, 0.3, True)
    pause_text()

def about_dialogue_games():
    return True

def about_dialogue_food():
    return True

def about_dialogue_tee():
    return True

def about_dialogue_pon():
    return True

def about_dialogue_jeremy():
    return True

def pause_text():
    pause("\n\nPress any key to continue.")
    return None

# initializing function to start the game, asking for input
def start_game():
    # intro_dialogue()
    main_dialogue()
    game_grid = grid_setup(board_size)
    sys.stdout.write("\n\n" + tee["talk"] + " ")
    sys.stdout.write(pon["talk"] + " ")
    subprocess.Popen('say -v Princess -r 100 "Let\'s begin!"', shell=True)
    subprocess.Popen('say -v Kathy -r 100 "Let\'s begin!"', shell=True)
    text_typer(None, None, None, "Let's begin!", 0.1, 0, False)
    time.sleep(0.6)
    clear_screen()
    show_grid(game_grid)
    ship_generator(board_size)
    guesses = 0
    sys.stdout.flush()
    while 1:
        if num_ships == 0:
            break
        if ship_hitting(board_size, game_grid) > 0:
            guesses += 1
    print "End game! You missed %d times." % guesses

"""""""""""""""
-----START-----
-----GAME!-----
"""""""""""""""

# clear the screen before starting
clear_screen()

try:
    start_game()

except KeyboardInterrupt:
    os.system('clear')
    subprocess.Popen('say -v Princess "Byeee! We\'ll see you later!"', shell=True)
    time.sleep(2.2)
    subprocess.call('say -v Kathy "Finally."', shell=True)
    sys.exit()
