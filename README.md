# EDMC-Timer
A plugin for the [Elite Dangerous Market Connector (EDMC)](https://github.com/EDCD/EDMarketConnector) to start a timer to track jumps and profit made during this time.

There are already similiar plugins (see [Acknowledgement](https://github.com/Kamiikaze/EDMC-Timer/blob/master/README.md#acknowledgement)), but as they only show "per hour" and dont display the time from the start of the measurement, 
I made this plugin. Most logical is copied from those plugins, except the timer, as this is my first plugin and I am pretty new into python lol.

## ToDo:
- [x] Count Profit (buy/sell)
- [x] Keep stats after stopping timer
- [x] Count Jumps
- [ ] Function to pause the timer

Open for suggestions!


## Install
Simply unzip **EDMC-Timer** into your plugins folder so it looks like this:

`plugins\EDMC-Timer-X.X.X\load.py`

and restart **EDMC**.


## Usage
- Press `Start` to start the timer. While running, it counts jumps and profit made.
- Press `Stop` to stop the timer. Additional jumps / profit won't add to the counter.
- If timer is stopped and you press `Start` again, all values reset.


## Config
Under `Settings > EDMC-Timer` there are 2 options to enable/disable the rows of Jumps / Income


## Compatibility
- **Python:** 3.9 and higher
- **EDMC:** 4.1.5 and higher


## Acknowledgement
- [EDMC-HourlyIncome](https://github.com/Exynom/EDMC-HourlyIncome) for Income calculation
- [EDMCJumpSpeed](https://github.com/inorton/EDMCJumpSpeed) for Jumps calculation


## Contact
[Github issues](https://github.com/Kamiikaze/EDMC-Timer/issues)
