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
    pause("\n\nPress any key to continue.")
    clear_screen()
    text_typer("Princess", "talk", 220, "Alrighty! ", 0.08, 0, True)
    text_typer("Princess", None, 230, "Do you know how to play?", 0.05, 0.02, False)
    text_typer("Kathy", "otalk", 160, "Oh my god, ", 0.075, 0.05, True)
    text_typer("Kathy", None, 190, "who doesn\\\'t know how to play battleship.", 0.055, 0.02, False)
    text_typer("Princess", "sad", 240, "Pon! ", 0.06, 0, True)
    text_typer("Princess", None, 200, "You cant just assume everyone ", 0.06, 0.3, False)
    text_typer("Princess", None, 130, "KNOWS ", 0.09, 0.01, False)
    text_typer("Princess", None, 220, "how to play battleship.", 0.06, 0.04, False)
    text_typer("Kathy", "loud", 120, "I kan, and I will.", 0.09, 0.3, True)
    text_typer("Princess", "dotdotdot", 100, "...", 0.3, 0, True)
    text_typer("Princess", "talk", 210, "Please dont mind Pon. ", 0.07, 0, True)
    text_typer("Princess", None, 210, "They can be grumpy sometimes.", 0.06, 0.025, False)
    pause("\n\nPress any key to continue.")
    clear_screen()

def help_dialogue():
    global talk_counter
    global help_counter
    while 1:
        clear_screen()
        if randint(0, 1) == 0:
            if help_counter > 1:
                text_typer("Princess", "talk", 210, "Did that help at all?", 0.06, 0, True)
            else:
                text_typer("Princess", "talk", 210, "What is up!", 0.07, 0, True)
        else:
            if help_counter > 1:
                text_typer("Kathy", "talk", 170, "Did that clarify for you?", 0.07, 0, True)
            else:
                text_typer("Kathy", "talk", 170, "So, ", 0.08, 0, True)
                text_typer("Kathy", None, 180, "what do you wanna do?", 0.055, 0.2, False)
        print "\n"
        sys.stdout.flush()
        choice = raw_input("\nTopics: help, about, play\n> ")
        if choice == "help":
            # clear_screen()
            # text_typer("Princess", "gasp", 210, "Oh!", 0.07, 0, True)
            # text_typer("Princess", "talk", 210, "It is perfectly normal to not have played battleship before.", 0.05, 0.5, True)
            # text_typer("Princess", "talk", 190, "I remember my first battleship game...", 0.06, 0, True)
            # text_typer("Princess", None, 150, " just like it was yester-", 0.048, 0, False)
            # text_typer("Kathy", "loud", 170, "Thats because it WAS yesterday.", 0.06, 0, True)
            # text_typer("Princess", "sad", 200, "Pon!", 0.06, 0.2, True)
            # text_typer("Princess", "tinysmile", 210, "Youre absolutely right!", 0.07, 1, True)
            # text_typer("Princess", "talk", 190, "That is why its so fresh in my mind.", 0.055, 0, True)
            # sys.stdout.flush()
            # pause("\n\nPress any key to continue.")
            # clear_screen()
            # text_typer("Kathy", "talk", 160, "So basically there is a grid.", 0.06, 0, True)
            # text_typer("Princess", "talk", 200, "Yes a grid mmm.", 0.06, 0, True)
            # text_typer("Kathy", "talk", 170, "And youre gonna guess where our ships are.", 0.052, 0, True)
            # text_typer("Princess", "yell", 210, "Just try us!", 0.06, 0, True)
            # text_typer("Kathy", "talk", 160, "...yeah and if you miss, ", 0.06, 0.4, True)
            # text_typer("Kathy", None, 170, "youll see a little dash on the board.", 0.06, 0, False)
            # text_typer("Princess", "oh", 210, "But if you hit...", 0.06, 0, True)
            # text_typer("Kathy", "loud", 160, "theres gonna be a big X on the battlefield!", 0.06, 0, True)
            # time.sleep(0.4)
            # clear_screen()
            # text_typer("Princess", "sad", 250, "Wait! ", 0.04, 0, True)
            # text_typer("Princess", None, 250, "Which one is the grid and what is the battlefield?", 0.04, 0.3, False)
            # text_typer("Kathy", "otalk", 170, "Oh.", 0.1, 0.5, True)
            # text_typer("Kathy", "neutral", 170, "Umm...", 0.1, 0.1, True)
            # text_typer("Kathy", "talk", 170, "Theyre the same thing.", 0.055, 0.1, True)
            # text_typer("Princess", "oh", 200, "Well what about the board?", 0.05, 0, True)
            # text_typer("Kathy", "talk", 170, "Also the same.", 0.06, 0, True)
            # text_typer("Princess", "smile", 200, " ", 0.8, 0.4, True)
            # text_typer("Princess", "talk", 200, "Im not sure I follow but okay!", 0.06, 0.8, True)
            # sys.stdout.flush()
            pause("\n\nPress any key to continue.")
            clear_screen()
            text_typer("Kathy", "talk", 160, "Anyways, ", 0.11, 0, True)
            text_typer("Kathy", None, 170, "each ship has 2 to 4 hits it can take.", 0.06, 0.15, False)
            text_typer("Princess", "talk", 200, "So if you make a hit, ", 0.055, 0.2, True)
            text_typer("Princess", None, 220, "the rest of the ship is nearby!", 0.05, 0, False)
            text_typer("Kathy", "otalk", 170, "We\\\'ll definitely let you know if one of our ships got sunk.", 0.05, 0.2, True)
            text_typer("Princess", "oh", 200, "That is...", 0.08, 0.1, True)
            text_typer("Princess", "yell", 230, "IF YOU CAN SINK OUR SHIPS!", 0.05, 0.2, True)
            sys.stdout.flush()
            pause("\n\nPress any key to continue.")
            clear_screen()
            text_typer("Kathy", "otalk", 165, "All of your guesses should be a letter then a number.", 0.05, 0, True)
            text_typer("Kathy", "talk", 160, "Like A1 ", 0.065, 0, True)
            text_typer("Kathy", "talk", 170, "or something.", 0.06, 1, False)
            text_typer("Princess", "talk", 180, "or B3!", 0.085, 0.3, True)
            text_typer("Kathy", "talk", 150, "You get the idea.", 0.075, 0.13, True)
            sys.stdout.flush()
            pause("\n\nPress any key to continue.")
            talk_counter += 1
            help_counter += 1
            continue
        elif choice == "about":
            talk_counter += 1
            continue
        elif choice == "play":
            clear_screen()
            if talk_counter == 0:
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


# initializing function to start the game, asking for input
def start_game():
    # intro_dialogue()
    help_dialogue()
    game_grid = grid_setup(board_size)
    sys.stdout.write("\n\n" + tee["talk"] + " ")
    sys.stdout.write(pon["talk"] + " ")
    subprocess.Popen('say -v Princess -r 100 "Let\'s begin!"', shell=True)
    subprocess.Popen('say -v Kathy -r 100 "Let\'s begin!"', shell=True)
    text_typer(None, None, None, "Let's begin!", 0.1, 0, False)
    time.sleep(0.5)
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
