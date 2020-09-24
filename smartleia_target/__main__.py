import code
import itertools
import sys
import time
import smartleia_target as sl
spinner = itertools.cycle(['-', '/', '|', '\\'])

leia = None

logo = r"""
  _________                      __  .____     ___________.___   _____   
 /   _____/ _____ _____ ________/  |_|    |    \_   _____/|   | /  _  \  
 \_____  \ /     \\__  \\_  __ \   __\    |     |    __)_ |   |/  /_\  \ 
 /        \  Y Y  \/ __ \|  | \/|  | |    |___  |        \|   /    |    \
/_______  /__|_|  (____  /__|   |__| |_______ \/_______  /|___\____|__  /
        \/      \/     \/                    \/        \/    TARGET   \/ 

        
"""


def reader_wait_for_card(target):
    """
        Wait for the smartcard to be inserted
    """
    print('Waiting for card to be inserted...\t',end='')
    while not(target.is_card_inserted()):
        time.sleep(0.1)
        sys.stdout.write(next(spinner))
        sys.stdout.flush()            
        sys.stdout.write('\b')
    print('OK')


if __name__ == "__main__":

    print(logo)
    target = sl.TargetController()
    reader_wait_for_card(target)
    target.reset()

    code.interact(
        local=locals(),
        banner="""

        The connection with the LEIA target test applet is opened.

        You have access to leia through the `target` variable.
        
        Type help(target) for commands lits and descriptions

        Type exit() or CTRL-D to exit.

        """,
    )

    target.close()
    sys.exit(0)
