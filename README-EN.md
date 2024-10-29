# PAWS Bot

[![Bot Link](https://img.shields.io/badge/Telegram-Bot_Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/PAWSOG_bot/PAWS?startapp=MevXkpYU)
[![Channel Link](https://img.shields.io/badge/Telegram-Channel_Link-blue?style=for-the-badge&logo=Telegram&logoColor=white)](https://t.me/+l3roJWT9aRNkMjUy)

---

## 📑 Table of Contents
1. [Description](#description)
2. [Key Features](#key-features)
3. [Installation](#installation)
   - [Quick Start](#quick-start)
   - [Manual Installation](#manual-installation)
4. [Settings](#settings)
5. [Support and Donations](#support-and-donations)
6. [Contact](#contact)

---

## 📜 Description
**PAWS Bot** is a powerful bot for Telegram that helps automate interaction with the PAWS bot. It supports multithreading, proxy integration, and session creation via QR codes.

---

## 🌟 Key Features
- 🔄 **Multithreading** — supports parallel processes to increase work speed
- 🔐 **Proxy binding to session** — allows secure work through proxy servers
- 📲 **Auto-account registration** — quick account registration via referral links
- 🎁 **Quest automation** — automatic completion and collection of quest rewards
- 📸 **Session creation via QR code** — fast and convenient session generation through a mobile app
- 📄 **Support for pyrogram session format (.session)** — easy integration with the Telegram API for session storage

---

## 🛠️ Installation

### Quick Start
1. **Download the project:**
   ```bash
   git clone https://github.com/Mffff4/qlyukerbot.git
   cd qlyukerbot
   ```

2. **Install dependencies:**
   - **Windows**:
     ```bash
     run.bat
     ```
   - **Linux**:
     ```bash
     run.sh
     ```

3. **Get API keys:**
   - Go to [my.telegram.org](https://my.telegram.org) and get your `API_ID` and `API_HASH`
   - Add this information to the `.env` file

4. **Run the bot:**
   ```bash
   python3 main.py --action 3  # Run the bot
   ```

### Manual Installation
1. **Linux:**
   ```bash
   sudo sh install.sh
   python3 -m venv venv
   source venv/bin/activate
   pip3 install -r requirements.txt
   cp .env-example .env
   nano .env  # Add your API_ID and API_HASH
   python3 main.py
   ```

2. **Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   copy .env-example .env
   python main.py
   ```

---

## ⚙️ Settings

| Setting               | Default Value          | Description                                                                  |
|----------------------|------------------------|------------------------------------------------------------------------------|
| **API_ID**           |                        | Unique application ID required for Telegram API                              |
| **API_HASH**         |                        | Application hash used for Telegram API authentication                        |
| **USE_PROXY_FROM_FILE**| False                | Use proxy from bot/config/proxies.txt file                                  |
| **REF_ID**           | "MevXkpYU"            | Referral code for registering new users                                     |
| **REQUEST_TIMEOUT**   | 20                    | HTTP request timeout in seconds                                             |
| **RETRY_DELAY**       | 3                     | Delay between retry attempts in case of error                               |
| **MAX_RETRIES**       | 5                     | Maximum number of request retry attempts                                    |
| **ENABLE_QUESTS**     | True                  | Enable/disable automatic quest completion                                   |
| **QUEST_CHECK_INTERVAL**| 600                 | Interval for checking new quests in seconds                                 |
| **DELAY_BETWEEN_QUESTS**| [3, 15]            | Minimum and maximum delay between quest completions in seconds              |

---

## 💰 Support and Donations

Support the development using cryptocurrencies:

| Currency              | Wallet Address                                                                     |
|----------------------|------------------------------------------------------------------------------------|
| Bitcoin (BTC)|bc1qt84nyhuzcnkh2qpva93jdqa20hp49edcl94nf6| 
| Ethereum (ETH)|0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
|TON|UQBlvCgM84ijBQn0-PVP3On0fFVWds5SOHilxbe33EDQgryz|
| Binance Coin (BNB)|0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
| Solana (SOL)|3vVxkGKasJWCgoamdJiRPy6is4di72xR98CDj2UdS1BE| 
| Ripple (XRP)|rPJzfBcU6B8SYU5M8h36zuPcLCgRcpKNB4| 
| Dogecoin (DOGE)|DST5W1c4FFzHVhruVsa2zE6jh5dznLDkmW| 
| Polkadot (DOT)|1US84xhUghAhrMtw2bcZh9CXN3i7T1VJB2Gdjy9hNjR3K71| 
| Litecoin (LTC)|ltc1qcg8qesg8j4wvk9m7e74pm7aanl34y7q9rutvwu| 
| Matic|0xc935e81045CAbE0B8380A284Ed93060dA212fa83| 
| Tron (TRX)|TQkDWCjchCLhNsGwr4YocUHEeezsB4jVo5| 

---

## 📞 Contact

If you have any questions or suggestions:
- **Telegram**: [Join our channel](https://t.me/+ap1Yd23CiuVkOTEy)

---

## ⚠️ Disclaimer

This software is provided "as is" without any warranties of any kind. By using this bot, you accept full responsibility for its use and any consequences that may arise.

The author is not responsible for:
- Any direct or indirect damages related to the use of the bot
- Possible violations of third-party service terms of use
- Account blocking or access restrictions

Use the bot at your own risk and in compliance with applicable laws and third-party service terms of use.

