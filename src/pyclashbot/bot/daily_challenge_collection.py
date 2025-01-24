from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.detection.image_rec import pixel_is_equal, check_region_for_color
from pyclashbot.utils.logger import Logger
import numpy
from pyclashbot.memu.client import save_screenshot, screenshot, click

from datetime import datetime
import time


def collect_daily_rewards_state(vm_index, logger, next_state):
    # First check if all rewards have already been collected
    if check_if_rewards_collected(vm_index):
        logger.change_status("All daily rewards have been collected")
        return next_state

    if not collect_all_daily_rewards(vm_index, logger):
        logger.change_status("Failed to collect daily rewards")
        return "restart"

    return next_state


def check_if_rewards_collected(vm_index):

    if not check_if_on_clash_main_menu(vm_index):
        return "restart"

    # Check each specified pixel for the checkmark
    region = [34, 201, 25, 20]
    if check_region_for_color(vm_index, region, (100, 239, 62)) is False:
        return False

    # If all pixels match, the checkmark is present
    return True


def collect_challenge_rewards(vm_index, logger, rewards) -> bool:
    # Ensure we are on the main menu of Clash
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            "Not on clash main at start of collect_challenge_rewards(). Returning False")
        return False

    # Open the daily rewards menu
    click(vm_index, 41, 206)
    time.sleep(2)

    # Collect rewards
    # Click positions to collect the rewards
    reward_positions = [(87, 196), (174, 197), (249, 198), (315, 210), (317, 519)]
    reward_messages = [
        "Collected 1st daily challenge reward (lucky drop)",
        "Collected 2nd daily challenge reward (crowns)",
        "Collected 3rd daily challenge reward (lucky drop)",
        "Collected 4th daily challenge reward (lucky drop)",
        "Collected 5th streak reward (lucky drop)",
    ]

    for i, (x, y) in enumerate(reward_positions):
        if rewards[i]:
            click(vm_index, x, y)
            logger.change_status(reward_messages[i])
            logger.add_daily_reward()
            time.sleep(1)

            # Close reward confirmation pop-ups
            if i == 1:  # For the crown reward in the 2nd slot
                click(vm_index, 10, 450, clicks=5, interval=0.33)
            else:  # For "lucky drop" rewards
                click(vm_index, 15, 450, clicks=8, interval=0.25)
                current_date = datetime.now().strftime("%d_%m_%Y")
                time.sleep(4)
                for _ in range(3):
                    time.sleep(1)
                    save_screenshot(vm_index, f"LuckyDrop_{i + 1}_{current_date}")
                logger.change_status(f"Saved screenshot of lucky drop reward {i + 1}")
                click(vm_index, 15, 450, clicks=5, interval=0.33)
                
            # Reopen the rewards menu only if necessary
            if i < len(rewards) - 1 and rewards[i + 1]:
                click(vm_index, 33, 212)
                time.sleep(2)

    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            "Not on clash main after collect_challenge_rewards(). Returning False")
        return False

    return True


def check_if_daily_rewards_button_exists(vm_index) -> bool:
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[181][17],
        iar[210][48],
        iar[200][36],
        iar[195][26],
        iar[205][63],
        iar[215][45],
        iar[226][31],
        iar[216][55],
        iar[236][66],
    ]

    colors = [
        [111, 75, 13],
        [136, 90, 23],
        [129, 91, 20],
        [118, 84, 16],
        [152, 102, 33],
        [132, 88, 21],
        [136, 96, 25],
        [147, 98, 27],
        [158, 101, 33],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=35):
            return True

    return False


def collect_all_daily_rewards(vm_index, logger) -> bool:
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            "Not on clash main at start of collect_daily_rewards(). Returning False")
        return False

    # if not check_if_daily_rewards_button_exists(vm_index):
    #     logger.change_status(
    #         "Daily rewards button doesn't exist. Assuming rewards already collected or not available.")
    #     return True

    rewards = check_which_rewards_are_available(vm_index, logger)
    if rewards is False:
        logger.change_status("Error checking which rewards are available")
        return False

    if not any(rewards):
        logger.change_status("No daily rewards available to collect")
        return True

    if not collect_challenge_rewards(vm_index, logger, rewards):
        logger.change_status("Failed to collect challenge rewards")
        return False

    return True


def check_which_rewards_are_available(vm_index, logger):
    logger.change_status("Checking which daily rewards are available")

    # if not on clash main, return False
    if check_if_on_clash_main_menu(vm_index) is not True:
        time.sleep(3)
        if check_if_on_clash_main_menu(vm_index) is not True:
            logger.change_status(
                "Not on clash main before check_which_rewards_are_available() "
            )

    # open daily rewards menu
    click(vm_index, 41, 206)
    time.sleep(20) #UI lag

    # check which rewards are available
    rewards = check_rewards_menu_pixels(vm_index)

    # click deadspace a bunch
    click(vm_index, 15, 450, clicks=3, interval=0.33)
    time.sleep(2)

    # if not on clash main, return False
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            "Not on clash main after check_which_rewards_are_available()"
        )
        return False

    positives = 0
    for _ in rewards:
        if _:
            positives += 1

    print(f"There are {positives} to collect")
    return rewards


def check_rewards_menu_pixels(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[163][112],  # Position for button 1 (1st lucky drop)
        iar[163][188],  # Position for button 2
        iar[163][263],  # Position for button 3 (2nd lucky drop)
        iar[163][334],  # Position for button 4 (3rd lucky drop)
        iar[490][303],  # Position for button 5 (streak lucky drop)
    ]

    # Check if green value is higher than 200 (the green claim button)
    rewards_available = [pixel[1] > 200 and pixel[0] < 150 and pixel[2] < 150  for pixel in pixels] 
    return rewards_available


if __name__ == "__main__":
    bs = check_rewards_menu_pixels(12)
    for b in bs:
        print(b)
