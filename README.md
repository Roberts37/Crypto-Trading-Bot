# Crypto-Trading-Bot

Tsunami is an automated cryptocurrency trading bot designed to execute trading strategies based on technical analysis and market conditions. Named Tsunami for the wild ride of day trading, please use at your own risk, I am not responsible for any losses occured for using this bot. This trading bot excels in trending markets, however it does strugle in flat markets. This README provides an overview of the Tsunami trading bot, including its features, usage, and key components.

## Features
Tsunami trading bot offers the following features:

- Multiple Timeframes: Uses short and long timeframes for in-depth technical analysis.
- Technical Indicators: Employs technical indicators such as GANN HILO, and ADX to make trading decisions.
- Position Management: Can open and close both long and short positions based on specific criteria.
- Risk Management: Includes risk control mechanisms like stop-loss levels.
- Leverage Management: Allows setting leverage for trading pairs.
- Continuous Monitoring: Monitors open positions and market conditions in real-time.
- Dynamic Symbol Selection: Dynamically selects symbols for trading based on market trends.
- Scheduler: Uses APScheduler for scheduling and executing trading actions at specific intervals.
- Multi-Instance Support: Capable of running multiple instances for trading different symbols simultaneously.

## Prerequisites
Before setting up and running the Tsunami trading bot, ensure you have the following prerequisites:

- Python 3.7 or higher.
- An API key and secret from your chosen cryptocurrency exchange platform, which should be kept secure and not shared publicly.
  
## Installation
To install Tsunami, follow these steps:

Clone this GitHub repository to your local machine:

- git clone https://github.com/yourusername/tsunami-trading-bot.git

Navigate to the project directory:

- cd tsunami-trading-bot

Edit the api.py file and provide your API key and secret from your cryptocurrency exchange platform:

- api_key = 'YOUR_API_KEY'
- api_secret = 'YOUR_API_SECRET'

## Configuration
In the tsunami.py script, you can configure trading settings, such as:

- Symbol selection: Define the cryptocurrency pairs you want to trade.
- Timeframes: Set the desired short and long timeframes for technical analysis.
- Risk management: Configure stop-loss levels for long and short positions.
- Leverage: Define the leverage you want to use for trading.
- You can further customize the bot's trading strategy by modifying the algorithm implemented in the algo method.

Usage
To start the Tsunami trading bot, run the following command:

python tsunami.py
The bot will begin executing its trading strategy based on the configured settings.

The bot's actions and trading results will be displayed in the terminal.

To stop the bot, press Ctrl+C in the terminal.

Note: Make sure to run the bot in a secure and controlled environment. Cryptocurrency trading involves risks, and it's essential to understand the bot's strategy and use it responsibly.
