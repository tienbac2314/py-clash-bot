"""
This module contains functions related to donating cards in Clash of Clans.
"""
import time
import random
import numpy
from typing import Literal
from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    check_if_on_profile_page,
    get_to_clan_tab_from_clash_main,
    handle_trophy_reward_menu,
    check_for_trophy_reward_menu,
)
from pyclashbot.detection.image_rec import (
    find_references,
    get_file_count,
    get_first_location,
    make_reference_image_list,
    pixel_is_equal,
    crop_image,
    condense_coordinates,
)
from pyclashbot.memu.client import screenshot, click, scroll_up
from pyclashbot.utils.logger import Logger
from pyclashbot.bot.nav import get_to_profile_page, wait_for_clash_main_menu


def find_claim_button(vm_index):
    """
    Finds the location of the claim button for the free gift in the clan page.

    Args:
        vm_index (int): The index of the virtual machine to search for the claim button.

    Returns:
        list[int] or None: The coordinates of the claim button if found, or None if not found.
    """
    folder_name = "claim_clan_button"
    size = get_file_count(folder_name)
    names = make_reference_image_list(size)

    locations = find_references(
        screenshot(vm_index),
        folder_name,
        names,
        0.79,
    )

    coord = get_first_location(locations)
    if coord is not None:
        return [coord[1], coord[0]]  # Return coordinates

    return None

global only_free
only_free = False
def donate_cards_state(vm_index, logger: Logger, next_state, free_donate_toggle: bool):
    """
    This function represents the state of donating cards in Clash of Clans.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object for logging.
        next_state: The next state to transition to.
    """
    logger.add_donate_attempt()

    donate_start_time = time.time()
    global only_free 
    only_free = free_donate_toggle

    # if not on main: return
    clash_main_check = check_if_on_clash_main_menu(vm_index)
    if clash_main_check is not True:
        logger.change_status(
            "Not on clash main for the start of request_state()")
        logger.log(
            "These are the pixels the bot saw after failing to find clash main:")
        # for pixel in clash_main_check:
        #     logger.log(f"   {pixel}")

        return "restart"

    # if logger says we're not in a clan, check if we are in a clan
    if logger.in_a_clan is False:
        logger.change_status("Checking if in a clan before donating")
        in_a_clan_return = donate_state_check_if_in_a_clan(vm_index, logger)
        if in_a_clan_return == "restart":
            logger.change_status(
                status="Error 05708425 Failure with check_if_in_a_clan"
            )
            return "restart"

        if not in_a_clan_return:
            return next_state
    else:
        print(
            f"Logger's in_a_clan value is: {logger.in_a_clan} so skipping check")

    # if in a clan, update logger's in_a_clan value
    logger.update_in_a_clan_value(True)
    print(f"Set Logger's in_a_clan value to: {logger.in_a_clan}!")

    # run donate cards main
    if donate_cards_main(vm_index, logger) is False:
        logger.log("Failure donating cards. Returning false")
        return "restart"

    # print time taken
    time_taken = str(time.time() - donate_start_time)[:4]
    logger.change_status(f"Finished donating cards in {time_taken}s")

    # return next state
    return next_state


def donate_state_check_pixels_for_clan_flag(vm_index) -> bool:
    iar = numpy.asarray(screenshot(vm_index))  # type: ignore

    pix_list = []
    for x_coord in range(80, 96):
        pixel = iar[445][x_coord]
        pix_list.append(pixel)

    for y_coord in range(437, 453):
        pixel = iar[y_coord][88]
        pix_list.append(pixel)

    # for every pixel in the pix_list: format to be of format [r,g,b]
    for index, pix in enumerate(pix_list):
        pix_list[index] = [pix[0], pix[1], pix[2]]

    for pix in pix_list:
        total = int(pix[0]) + int(pix[1]) + int(pix[2])

        if total < 130:
            return True

        if total > 170:
            return True

    return False


def donate_state_check_if_in_a_clan(
    vm_index, logger: Logger
) -> bool | Literal["restart"]:
    # if not on clash main, return
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(status="ERROR 385462623 Not on clash main menu")
        return "restart"

    # get to profile page
    if get_to_profile_page(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 9076092860923485 Failure with get_to_profile_page"
        )
        return "restart"

    # check pixels for in a clan
    in_a_clan = donate_state_check_pixels_for_clan_flag(vm_index)

    # print clan status
    if not in_a_clan:
        logger.change_status("Not in a clan, so can't request!")

    # click deadspace to leave
    click(vm_index, 15, 450)
    if wait_for_clash_main_menu(vm_index, logger) is False:
        logger.change_status(
            status="Error 87258301758939 Failure with wait_for_clash_main_menu"
        )
        return "restart"

    return in_a_clan


def donate_cards_main(vm_index, logger: Logger) -> bool:
    # get to clan chat page
    logger.change_status("Getting to clan tab to donate cards")
    if get_to_clan_tab_from_clash_main(vm_index, logger) is False:
        return False

    # click jump to bottom button
    click(vm_index, 385, 488)
    time.sleep(2)

    logger.change_status("Starting donate sequence")
    for _ in range(2):
        # click donate buttons that exist on this page, then scroll a little
        for _ in range(3):
            loops = 0
            # Try to claim free gift if available
            claim_button_coord = find_claim_button(vm_index)
            if claim_button_coord:
                logger.log(
                    "Claim button found. Claiming free gift from clan mate.")
                click(vm_index, *claim_button_coord)
                time.sleep(3)
            while find_and_click_donates(vm_index, logger) is True:
                logger.change_status("Found a donate button")
                loops += 1
                if loops > 50:
                    return False
                time.sleep(0.5)

            logger.change_status(
                "Scrolling up to search for more donate requests")
            scroll_up(vm_index)
            time.sleep(1)

        # click the more requests button that may exist
        click(vm_index, 48, 132)
        time.sleep(1)

        # click deadspace
        click(vm_index, 10, 233)
        time.sleep(0.33)

    # get to clash main
    logger.change_status("Returning to clash main after donating")
    click(vm_index, 175, 600, clicks=1)
    time.sleep(5)

    # handle geting stuck on trophy road screen
    if check_for_trophy_reward_menu(vm_index):
        handle_trophy_reward_menu(vm_index, logger)
        time.sleep(2)

    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.log("Failed to get to clash main after doanting! Retsrating")
        return False
    time.sleep(3)

    return True


def find_and_click_donates(vm_index, logger):
    logger.change_status("Searching for donate buttons...")
    coords = find_donate_buttons(vm_index)

    found_donates = False
    start_time = time.time()
    timeout = 30  # s
    for coord in coords:
        # if coord is too high
        if coord[1] < 108:
            print("Found a donate button but its too high to do anything with")
            continue

        # if coord is in range, click it until its grey
        while check_for_positive_donate_button_coords(vm_index, coord):
            # timeout check
            if time.time() - start_time > timeout:
                logger.change_status("Timed out while donating... Restarting")
                return "restart"

            # do clicking, increment counter, toggle found_donates
            click(vm_index, coord[0], coord[1])
            logger.change_status("Donated a card!")
            found_donates = True
            logger.add_donate()
            time.sleep(0.5)

    return found_donates


def find_donate_buttons(vm_index):
    start_time = time.time()
    coords = []

    for _ in range(10):
        try:
            left = 238
            right = 375
            top = 80
            bottom = 475

            image = screenshot(vm_index)

            t = random.randint(top, bottom)
            width = right-left
            region = [left, t, width, 100]

            image = crop_image(image, region)

            global only_free
            if only_free: coord = find_donate_button_for_free(image, vm_index, region)
            else: coord = find_donate_button(image) 

            if coord is None:
                continue

            coord = [coord[0] + region[0], coord[1] + region[1]]

            # adjust coord to make it more central to the icon
            coord = [coord[0] + 37, coord[1] + 7]

            coords.append(coord)
        except:
            pass

    time_taken = str(time.time() - start_time)[:5]
    print(f"Finished find_donate_buttons() in {time_taken}s")
    return condense_coordinates(coords, distance_threshold=15)

def find_donate_button_for_free(image, vm_index, region):
    """method to find the donate icon for FREE in a cropped image"""

    coord = find_donate_button(image) #[y,x]
    # print(f"x: {coord[1] + region[0]}, y: {coord[0] + region[1]}")
    if coord != None:
        # print("found donate button, checking if it's free")
        x = coord[1] + region[0]
        y = coord[0] + region[1]
        # print(f"left: {x-200} right: {x-80} top:{y-30}, bottom: {y+30}")
        free_region = [x - 200, y - 30, 120, 60]
        free_image = screenshot(vm_index)
        free_image = crop_image(free_image, free_region)
        
        folder = "free_donate_icon"

        names = make_reference_image_list(get_file_count(folder))

        locations: list[list[int] | None] = find_references(
            free_image,
            folder,
            names,
            tolerance=0.88,
        )

        free_coord = get_first_location(locations)

        if free_coord is None:
            # print("it's not free")
            return None
        else: 
            # print("it is!")
            return [coord[1], coord[0]]
    return None


def find_donate_button(image):
    """method to find the donate icon in a cropped image"""

    folder = "donate_button_icon"

    names = make_reference_image_list(get_file_count(folder))

    locations: list[list[int] | None] = find_references(
        image,
        folder,
        names,
        tolerance=0.88,
    )

    coord = get_first_location(locations)

    if coord is None:
        return None

    return [coord[1], coord[0]]


def check_for_positive_donate_button_coords(vm_index, coord):
    # if pixel is too high, always return False

    iar = screenshot(vm_index)

    positive_color = [58, 228, 73]

    pixels = []
    region_width = 50
    region_height = 50
    c1 = [int(coord[0] - region_width / 2), int(coord[1] - region_height / 2)]
    for x in range(region_width):
        for y in range(region_height):
            pixels.append(iar[c1[1] + y, c1[0] + x])

    positive_count = 0
    for pixel in pixels:
        if pixel_is_equal(pixel, positive_color, tol=20):
            positive_count += 1

    if (positive_count) > 5:
        return True
    return False


if __name__ == "__main__":
    while 1:
        print(find_donate_buttons(12))

    # print(find_donate_button(screenshot(12)))
