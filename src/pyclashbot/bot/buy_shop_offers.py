import time
import numpy

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_shop_page_from_clash_main,
)
from pyclashbot.detection.image_rec import (
    find_references,
    get_first_location,
    get_file_count,
    make_reference_image_list,
    pixel_is_equal,
)
from pyclashbot.memu.client import (
    screenshot,
    click,
    scroll_down_slowly_in_shop_page,
)

from pyclashbot.utils.logger import Logger

SHOP_BUY_TIMEOUT = 35


def buy_shop_offers_state(
    vm_index: int,
    logger: Logger,
    gold_buy_toggle: bool,
    free_offers_toggle: bool,
    next_state: str,
):
    print("Entering buy_shop_offers_state()")
    print(f"gold_buy_toggle: {gold_buy_toggle}")
    print(f"free_offers_toggle: {free_offers_toggle}")

    logger.add_shop_buy_attempt()

    # if not on clash main, return False
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            "Not on clash main to being buying offers. Returning restart"
        )
        return "restart"

    if (
        buy_shop_offers_main(
            vm_index,
            logger,
            gold_buy_toggle,
            free_offers_toggle,
        )
        is not True
    ):
        logger.change_status("Failed to buy offers. Returning restart")
        return "restart"

    time.sleep(3)

    # if not on clash main, return False
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status("Not on clash main after buying offers. Returning restart")
        return "restart"

    return next_state


def buy_shop_offers_main(
    vm_index: int,
    logger: Logger,
    gold_buy_toggle: bool,
    free_offers_toggle: bool,
) -> bool:
    # get to shop page
    logger.change_status("Getting to shop page to buy offers")
    if get_to_shop_page_from_clash_main(vm_index, logger) is False:
        logger.change_status("Failed to get to shop page to buy offers")
        return False

    # scroll incrementally while searching for rewards, clicking and buying any rewards found

    purchase_total = 0

    start_time = time.time()
    done_buying = False
    logger.change_status("Starting to buy offers")
    scroll_time = 0
    while 1 and done_buying is False:
        if time.time() - start_time > SHOP_BUY_TIMEOUT:
            break
        
        # get to daily deal section
        if scroll_time % 8 == 0:
            # click the shop page button to get to gold offers
            click(vm_index, 49, 584)
            time.sleep(2)

        # scroll a little
        logger.change_status("Searching for offers to buy")
        # print("Time taken in shop: ", str(time.time() - start_time)[:5])
        scroll_down_slowly_in_shop_page(vm_index)
        scroll_time += 1
        time.sleep(1)

        if gold_buy_toggle or free_offers_toggle:
            while (
                buy_offers_from_this_shop_page(
                    vm_index, logger, gold_buy_toggle, free_offers_toggle
                )
                is True
                and done_buying is False
            ):
                purchase_total += 1
                scroll_time = 0
                logger.change_status("Bought an offer from the shop!")
                time.sleep(2)
                start_time = time.time()

                # if only free offers are toggled, AND purchase total is 1, then it's done
                if free_offers_toggle and not gold_buy_toggle and purchase_total == 1:
                    print("only free offers toggles and purchase total is 1, breaking")
                    done_buying = True
                    break

                # if both modes are toggled, and total is 6, break
                if gold_buy_toggle and free_offers_toggle and purchase_total == 6:
                    print("both modes toggled and purchase total is 6, breaking")
                    done_buying = True
                    break

                # if only gold offers are toggled, and purchase total is 6, break
                if gold_buy_toggle and not free_offers_toggle and purchase_total == 5:
                    print("only gold offers toggled and purchase total is 6, breaking")
                    done_buying = True
                    break

    logger.change_status("Done buying offers. Returning to clash main")

    # get to clash main from shop page
    click(vm_index, 245, 596)
    time.sleep(4)

    return True


def search_for_free_purchases(vm_index):
    """method to find the free offer icon image in the shop pages"""

    folder_name = "free_offer_icon"
    size = get_file_count(folder_name)
    names = make_reference_image_list(size)
    locations = find_references(
        screenshot(vm_index),
        folder_name,
        names,
        0.88,
    )
    coord = get_first_location(locations)
    if coord is None:
        return None
    return [coord[1], coord[0]]


def search_for_gold_purchases(vm_index):
    """method to find the offers for gold icon image in the shop pages"""

    folder_name = "offers_for_gold"
    size = get_file_count(folder_name)
    names = make_reference_image_list(size)
    locations = find_references(
        screenshot(vm_index),
        folder_name,
        names,
        0.88,
    )
    coord = get_first_location(locations)
    if coord is None:
        return None
    return [coord[1], coord[0]]


def buy_offers_from_this_shop_page(
    vm_index, logger, gold_buy_toggle, free_offers_toggle
):
    coord = None

    if gold_buy_toggle:
        coord = search_for_gold_purchases(vm_index)

    # if no gold purchases, find a free purchase
    if coord is None and free_offers_toggle:
        coord = search_for_free_purchases(vm_index)

    # if there are no purchases at this point, return False
    if coord is None:
        return False

    # click the location of the 'cards for gold' icon
    click(vm_index, coord[0], coord[1])
    time.sleep(2)

    # click the second 'buy' button
    click(vm_index, 200, 433)
    click(vm_index, 204, 394)
    logger.add_shop_offer_collection()
    time.sleep(2)

    # click deadspace to close this offer
    while not check_if_on_shop_page(vm_index):
        click(vm_index, 15, 200)

    return True


def check_if_on_shop_page(vm_index):
    iar = numpy.asarray(screenshot(vm_index))

    pixels = [
        iar[582][19],
        iar[599][108],
        iar[595][13],
    ]
    colors = [
        [138, 103, 70],
        [143, 109, 74],
        [142, 108, 73],
    ]

    for i, p in enumerate(pixels):
        # print(p)
        if not pixel_is_equal(colors[i], p, tol=10):
            return False
    return True


def shop_buy_tester():
    vm_index = 12
    logger = Logger(None, None)
    gold_buy_toggle = True
    free_offers_toggle = True

    print(
        buy_shop_offers_main(
            vm_index,
            logger,
            gold_buy_toggle,
            free_offers_toggle,
        )
    )


if __name__ == "__main__":
    shop_buy_tester()
