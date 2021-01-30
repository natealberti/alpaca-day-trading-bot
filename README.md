# alpaca-day-trading-bot
Bot that buys/sells stocks through the Alpaca API

This bot has some very simple set of conditions it runs though. It starts in the buying phase, and chooses a random stock from a pre-selected list to choose from. Every five seconds the bot re-evaluates the price of the selected stock, if it falls under a certain price it will purchase about $2000 of shares (or whatever the target price is set to). Attached to this buy order is a stop price and a limit price, to indicate at what price Alpaca will issue a sell. These constants are able to be changed to get different results.
Every cycle the bot updates the console to what is going on, to help give more clarity.
The only problem with this bot is that it WILL mark you as a pattern day trader. I was not aware of this when developing it, so I can't get much use out of it and bug testing was very tedious. I'm planning on making a swing-trading bot later, so that PDT rules won't apply...
This was only tested using the paper trading side of Alpaca, but it should work just the same for live trading. Just insert both keys from the Alpaca account into the code and get it started.
