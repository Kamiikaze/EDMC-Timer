import time
import logging
import tkinter as tk
import myNotebook as nb
import sys

from config import appname, config
from typing import Optional
from l10n import Locale

# For compatibility with pre-5.0.0
if not hasattr(config, 'get_int'):
    config.get_int = config.getint

if not hasattr(config, 'get_str'):
    config.get_str = config.get

if not hasattr(config, 'get_bool'):
    config.get_bool = lambda key: bool(config.getint(key))

if not hasattr(config, 'get_list'):
    config.get_list = config.get


PLUGIN_NAME = "zEDMC-Timer"
VERSION = '1.0.0'

logger = logging.getLogger(f"{appname}.{PLUGIN_NAME}")
this = sys.modules[__name__]


running = False
start_time = None
timer_label = None
jumps_made = 0
income_earned = 0

this.formatted_time = None
this.show_jumps = None
this.show_income = None


def start_timer():
    global start_time, running
    if not running:
        running = True
        
        start_time = time.time()
        this.jumps_val["text"] = 0
        this.income_val["text"] = "0 Cr"
        
        update_timer()
    else:
        logger.info("Timer is already running.")

def stop_timer():
    global running
    if running:
        running = False
        timer_label.config(text=f"Stopped Time: {this.formatted_time}")
    else:
        logger.info("No timer is running.")

def update_timer():
    if running:
        elapsed_time = time.time() - start_time
        this.formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
        timer_label.config(text=f"Elapsed Time: {this.formatted_time}")
        timer_label.after(1000, update_timer)

def plugin_app(parent):
    global timer_label

    frame = tk.Frame(parent)
    
    timer_label = tk.Label(frame, text="Time: 00:00:00")
    timer_label.grid(row=0, column=0, columnspan=4)
    
    this.jumps_label = tk.Label(frame, text="Jumps:", justify=tk.LEFT)
    this.jumps_val = tk.Label(frame, text=jumps_made, justify=tk.RIGHT)
    if config.getint("show_jumps"):
        this.jumps_label.grid(row=1, column=0, sticky=tk.W)
        this.jumps_val.grid(row=1, column=3, sticky=tk.E)
    
    this.income_label = tk.Label(frame, text="Income:", justify=tk.LEFT)
    this.income_val = tk.Label(frame, text="{inc} Cr".format(inc = income_earned), justify=tk.RIGHT)
    if config.getint("show_income"):
        this.income_label.grid(row=2, column=0, sticky=tk.W)
        this.income_val.grid(row=2, column=3, sticky=tk.E)


    start_button = tk.Button(frame, text="Start", command=start_timer)
    start_button.grid(row=4, column=0)

    stop_button = tk.Button(frame, text="Stop", command=stop_timer)
    stop_button.grid(row=4, column=3)
    
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)
    frame.columnconfigure(2, weight=1)
    frame.columnconfigure(3, weight=1)

    return frame

def increment_jumps():
    global jumps_made
    if running:
        jumps_made += 1
        this.jumps_val["text"] = jumps_made
    if this.show_jumps:
        logger.info(f"Jumps Made: {jumps_made}")

def add_income(amount):
    global income_earned
    if running:
        income_earned += amount
        this.income_val["text"] = "{inc} Cr".format(inc = Locale.stringFromNumber(income_earned, 0))
    if this.show_income:
        logger.info(f"Income Earned: {income_earned}")

def plugin_prefs(parent: nb.Notebook, cmdr: str, is_beta: bool) -> Optional[tk.Frame]:
    """
    Return a TK Frame for adding to the EDMarketConnector settings dialog.
    """
    frame = nb.Frame(parent)
    nb.Label(frame, text=f'{PLUGIN_NAME} v{VERSION}').grid(row=0, columnspan=2, padx=5, pady=2, sticky=tk.W)

    # Set the variables to their saved states
    this.show_jumps = tk.IntVar(value=config.getint("show_jumps"))
    this.show_income = tk.IntVar(value=config.getint("show_income"))

    nb.Checkbutton(frame, text="Display Jumps Made", variable=this.show_jumps).grid(row=1, columnspan=2, padx=5, pady=2, sticky=tk.W)
    nb.Checkbutton(frame, text="Display Income Earned", variable=this.show_income).grid(row=2, columnspan=2, padx=5, pady=2, sticky=tk.W)

    return frame

def prefs_changed(cmdr: str, is_beta: bool) -> None:
    """
    Save settings.
    """
    config.set('show_jumps', this.show_jumps.get())
    config.set('show_income', this.show_income.get())
    
    if not this.show_jumps.get():
        this.jumps_label.grid_forget()
        this.jumps_val.grid_forget()
    else:
        this.jumps_label.grid(row=1, column=0, sticky=tk.W)
        this.jumps_val.grid(row=1, column=3, sticky=tk.E)
    
    if not this.show_income.get():
        this.income_label.grid_forget()
        this.income_val.grid_forget()
    else:
        this.income_label.grid(row=2, column=0, sticky=tk.W)
        this.income_val.grid(row=2, column=3, sticky=tk.E)

def plugin_start3(plugin_dir):
    # Initialize any necessary resources when the plugin starts
    logger.info(f"{PLUGIN_NAME} Started")
    return PLUGIN_NAME

def plugin_stop():
    # Clean up resources when the plugin stops
    global running
    running = False
    logger.info(f"{PLUGIN_NAME} Stopped")

def journal_entry(cmdr: str, is_beta: bool, system: str, station: str, entry: dict[str, any], state: dict[str, any]) -> Optional[str]:

    if entry['event'] == 'FSDJump':
        # We arrived at a new system!
        if 'StarPos' in entry:
            logger.info(f'Arrived at {entry["StarSystem"]} {entry["StarPos"]}')
            increment_jumps()
    
    if "event" in entry:
        # ! trading
        if "MarketSell" in entry["event"]:
            add_income(entry["TotalSale"])
        elif "MarketBuy" in entry["event"]:
            add_income(-entry["TotalCost"])
        elif "BuyTradeData" in entry["event"]:
            add_income(-entry["Cost"])
        # ! refuel/repair/restock
        elif "BuyAmmo" in entry["event"]:
            add_income(-entry["Cost"])
        elif "BuyDrones" in entry["event"]:
            add_income(-entry["TotalCost"])
        elif "SellDrones" in entry["event"]:
            add_income(entry["TotalSale"])
        elif "RefuelAll" in entry["event"]:
            add_income(-entry["Cost"])
        elif "RefuelPartial" in entry["event"]:
            add_income(-entry["Cost"])
        elif "Repair" in entry["event"]:
            add_income(-entry["Cost"])
        elif "RepairAll" in entry["event"]:
            add_income(-entry["Cost"])
        elif "RestockVehicle" in entry["event"]:
            add_income(-entry["Cost"])
        # ! shipyard/outfitting/engineering
        elif "ModuleBuy" in entry["event"]:
            add_income(-entry["Buyprice"])
            if "SellItem" in entry:
                add_income(entry["SellPrice"])
        elif "ModuleSell" in entry["event"]:
            add_income(entry["SellPrice"])
        elif "ModuleSellRemote" in entry["event"]:
            add_income(entry["SellPrice"])
        elif "FetchRemoteModule" in entry["event"]:
            add_income(-entry["TransferCost"])
        elif "ShipyardBuy" in entry["event"]:
            add_income(-entry["ShipPrice"])
            if "SellOldShip" in entry:
                add_income(entry["SellPrice"])
        elif "ShipyardSell" in entry["event"]:
            add_income(entry["ShipPrice"])
        elif "ShipyardTransfer" in entry["event"]:
            add_income(-entry["TransferPrice"])
        elif "EngineerContribution" in entry["event"] and "Credits" in entry["Type"]:
            add_income(-entry["Quantity"])
        # ! fees
        elif "PayBounties" in entry["event"]:
            add_income(-entry["Amount"])
        elif "PayFines" in entry["event"]:
            add_income(-entry["Amount"])
        elif "PayLegacyFines" in entry["event"]:
            add_income(-entry["Amount"])
        # ! combat
        elif "RedeemVoucher" in entry["event"]:
            add_income(entry["Amount"])
        # ? These are probably logged upon award of bond/voucher and not upon payment; Instead, RedeemVoucher is logged upon payment
        # elif "Bounty" in entry["event"]:
        #     add_income(entry["TotalReward"])
        # elif "CapShipBond" in entry["event"]:
        #     add_income(entry["Reward"])
        # elif "FactionKillBond" in entry["event"]:
        #     add_income(entry["Reward"])
        # ! exploration
        elif "BuyExplorationData" in entry["event"]:
            add_income(-entry["Cost"])
        elif "SellExplorationData" in entry["event"]:
            add_income(entry["TotalEarnings"])
        # ! missions/community goals/search and rescue
        elif "CommunityGoalReward" in entry["event"]:
            add_income(entry["Reward"])
        elif "SearchAndRescue" in entry["event"]:
            add_income(entry["Reward"])
        elif "MissionCompleted" in entry["event"]:
            if "Dontation" in entry:
                add_income(-entry["Dontation"])
            else:
                add_income(entry["Reward"])
        # ! npc crew
        elif "CrewHire" in entry["event"]:
            add_income(-entry["Cost"])
        elif "NpcCrewPaidWage" in entry["event"]:
            add_income(-entry["Amount"])
        # ! rebuy
        elif "SellShipOnRebuy" in entry["event"]:
            add_income(entry["ShipPrice"])
        elif "Resurrect" in entry["event"]:
            add_income(-entry["Cost"])
        # ! powerplay
        elif "PowerplayFastTrack" in entry["event"]:
            add_income(-entry["cost"])
        elif "PowerplaySalary" in entry["event"]:
            add_income(entry["Amount"])