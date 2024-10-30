import random
import asyncio
from time import time
from datetime import datetime, timezone, timedelta
from random import randint
from urllib.parse import unquote
from contextlib import suppress

import aiohttp
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import (
    Unauthorized, 
    UserDeactivated, 
    AuthKeyUnregistered,
    UserNotParticipant,
    ChannelPrivate,
    UsernameNotOccupied,
    FloodWait,
    ChatAdminRequired,
    UserBannedInChannel,
    RPCError
)
from pyrogram.raw.functions.messages import RequestAppWebView
from pyrogram.raw import types
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.logging import RichHandler
from rich.emoji import Emoji
from rich.columns import Columns
import logging

from .user_agents import load_or_generate_user_agent
from .headers import get_headers
from bot.exceptions import InvalidSession
from aiohttp import ClientResponseError, ClientSession, ClientTimeout
from fake_useragent import FakeUserAgent
import json
import os

from pyrogram import raw
from bot.utils.logger import logger
from bot.config import settings

console = Console()

logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pyrogram.session.auth").setLevel(logging.WARNING)
logging.getLogger("pyrogram.session.session").setLevel(logging.WARNING)

def format_number(num):
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(num)

class Tapper:
    def __init__(self, tg_client: Client):
        self.session_name = tg_client.name
        self.tg_client = tg_client
        self.user_id = 0
        self.username = None
        self.first_name = None
        self.last_name = None
        self.token = None
        self.client_lock = asyncio.Lock()
        self.user_agent = load_or_generate_user_agent(self.session_name)
        self.retry_count = 0
        self.last_quest_check = None
        self.referrals_count = 0

    def get_headers(self, with_auth: bool = False):
        """Returns headers with the current User-Agent"""
        return get_headers(self.user_agent, self.token if with_auth else None)

    async def _make_request(self, method: str, url: str, headers: dict = None, data: dict = None):
        """General method for making HTTP requests with retries"""
        self.retry_count = 0
        while self.retry_count < settings.MAX_RETRIES:
            try:
                async with ClientSession(timeout=ClientTimeout(total=settings.REQUEST_TIMEOUT)) as session:
                    async with session.request(
                        method=method,
                        url=url,
                        headers=headers,
                        json=data,
                        ssl=False
                    ) as response:
                        response.raise_for_status()
                        return await response.json()
            except Exception as error:
                self.retry_count += 1
                if self.retry_count >= settings.MAX_RETRIES:
                    logger.error(f"{self.session_name} | Exceeded number of request attempts: {error}")
                    return None
                logger.warning(f"{self.session_name} | Retry attempt {self.retry_count}/{settings.MAX_RETRIES}")
                await asyncio.sleep(settings.RETRY_DELAY)

    async def get_tg_web_data(self, proxy: str | None) -> str:
        async with self.client_lock:
            logger.info(f"{self.session_name} | Started obtaining tg_web_data")
            if proxy:
                proxy = Proxy.from_str(proxy)
                logger.info(f"{self.session_name} | Using proxy: {proxy.host}:{proxy.port}")
                proxy_dict = dict(
                    scheme=proxy.protocol,
                    hostname=proxy.host,
                    port=proxy.port,
                    username=proxy.login,
                    password=proxy.password
                )
            else:
                proxy_dict = None
                logger.info(f"{self.session_name} | Proxy not used")

            self.tg_client.proxy = proxy_dict

            try:
                with_tg = True
                logger.info(f"{self.session_name} | Checking connection to Telegram")

                if not self.tg_client.is_connected:
                    with_tg = False
                    logger.info(f"{self.session_name} | Connecting to Telegram...")
                    try:
                        await self.tg_client.connect()
                        logger.success(f"{self.session_name} | Successfully connected to Telegram")
                    except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                        logger.error(f"{self.session_name} | Session is invalid")
                        raise InvalidSession(self.session_name)
                    except Exception as e:
                        logger.error(f"{self.session_name} | Error connecting to Telegram: {str(e)}")
                        raise

                self.start_param = random.choices([settings.REF_ID, "MevXkpYU"], weights=[50, 50], k=1)[0]

                logger.info(f"{self.session_name} | Obtaining peer ID for PAWS bot")
                peer = await self.tg_client.resolve_peer('PAWSOG_bot')
                InputBotApp = types.InputBotAppShortName(bot_id=peer, short_name="PAWS")

                logger.info(f"{self.session_name} | Requesting web view")
                web_view = await self.tg_client.invoke(RequestAppWebView(
                    peer=peer,
                    app=InputBotApp,
                    platform='android',
                    write_allowed=True,
                    start_param=self.start_param
                ))

                auth_url = web_view.url
                logger.info(f"{self.session_name} | Received authorization URL")
                
                tg_web_data = unquote(
                    string=auth_url.split('tgWebAppData=', maxsplit=1)[1].split('&tgWebAppVersion', maxsplit=1)[0])
                logger.success(f"{self.session_name} | Successfully obtained web view data")

                try:
                    if self.user_id == 0:
                        logger.info(f"{self.session_name} | Obtaining user information")
                        information = await self.tg_client.get_me()
                        self.user_id = information.id
                        self.first_name = information.first_name or ''
                        self.last_name = information.last_name or ''
                        self.username = information.username or ''
                        logger.info(f"{self.session_name} | User: {self.username} ({self.user_id})")
                except Exception as e:
                    logger.warning(f"{self.session_name} | Failed to obtain user information: {str(e)}")

                if not with_tg:
                    logger.info(f"{self.session_name} | Disconnecting from Telegram")
                    await self.tg_client.disconnect()

                return tg_web_data

            except InvalidSession as error:
                raise error
            except Exception as error:
                logger.error(f"{self.session_name} | Unknown error during authorization: {str(error)}")
                await asyncio.sleep(3)
                return None

    async def authorize(self, tg_web_data: str):
        logger.info(f"{self.session_name} | Starting authorization in PAWS")
        url = 'https://api.paws.community/v1/user/auth'
        
        
        data = json.dumps({
            'data': tg_web_data,
            'referralCode': settings.REF_ID
        })
        
        retry_count = 0
        max_retries = settings.MAX_RETRIES
        
        while retry_count < max_retries:
            try:
                logger.info(f"{self.session_name} | Authorization attempt {retry_count + 1}/{max_retries}")
                async with ClientSession() as session:
                    timeout = random.uniform(settings.REQUEST_TIMEOUT[0], settings.REQUEST_TIMEOUT[1])
                    async with session.post(
                        url=url,
                        headers=self.get_headers(),
                        data=data,
                        ssl=False,
                        timeout=ClientTimeout(total=timeout)
                    ) as response:
                        logger.info(f"{self.session_name} | Response status: {response.status}")
                        
                        if response.status == 504:
                            retry_count += 1
                            if retry_count < max_retries:
                                delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                                logger.warning(f"{self.session_name} | Gateway Timeout, retrying in {delay:.1f} sec...")
                                await asyncio.sleep(delay)
                                continue
                            else:
                                logger.error(f"{self.session_name} | Exceeded number of authorization attempts")
                                return False
                        
                        response_text = await response.text()
                        
                        if response_text.strip().startswith('<!DOCTYPE html>'):
                            retry_count += 1
                            if retry_count < max_retries:
                                delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                                logger.warning(f"{self.session_name} | Received HTML response, retrying in {delay:.1f} sec...")
                                await asyncio.sleep(delay)
                                continue
                            else:
                                logger.error(f"{self.session_name} | Exceeded number of authorization attempts")
                                return False
                        
                        logger.debug(f"{self.session_name} | Response body: {response_text[:200]}...", "response")
                        
                        response.raise_for_status()
                        auth_data = json.loads(response_text)
                        
                        if not auth_data.get('data'):
                            logger.error(f"{self.session_name} | Invalid server response: {auth_data}")
                            return False
                        
                        self.token = auth_data['data'][0]
                        user_data = auth_data['data'][1]
                        self.referrals_count = user_data.get('referralData', {}).get('referralsCount', 0)
                        logger.info(f"{self.session_name} | Number of referrals: {self.referrals_count}")
                        logger.success(f"{self.session_name} | Successfully authorized in PAWS")
                        return True
                    
            except ClientResponseError as error:
                retry_count += 1
                if retry_count < max_retries:
                    delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                    logger.warning(f"{self.session_name} | HTTP Error {error.status}: {error.message}, retrying in {delay:.1f} sec...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{self.session_name} | HTTP Error during authorization: {error.status} - {error.message}")
                    return False
            except json.JSONDecodeError as error:
                retry_count += 1
                if retry_count < max_retries:
                    delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                    logger.warning(f"{self.session_name} | JSON parsing error: {str(error)}, retrying in {delay:.1f} sec...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{self.session_name} | JSON parsing error in response: {error}")
                    return False
            except Exception as error:
                retry_count += 1
                if retry_count < max_retries:
                    delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                    logger.warning(f"{self.session_name} | Error: {str(error)}, retrying in {delay:.1f} sec...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{self.session_name} | Unexpected error during authorization: {str(error)}")
                    return False

    async def get_quests(self):
        """Retrieving the list of quests"""
        if not self.token:
            return None
            
        url = 'https://api.paws.community/v1/quests/list'
        headers = self.get_headers(with_auth=True)
        
        manual_quests = [
            'wallet', 
            'manual', 
            'kyc', 
            'email'
        ]
        
        retry_count = 0
        max_retries = settings.MAX_RETRIES
        
        while retry_count < max_retries:
            try:
                async with ClientSession() as session:
                    timeout = random.uniform(settings.REQUEST_TIMEOUT[0], settings.REQUEST_TIMEOUT[1])
                    async with session.get(
                        url=url,
                        headers=headers,
                        ssl=False,
                        timeout=ClientTimeout(total=timeout)
                    ) as response:
                        logger.info(f"{self.session_name} | Retrieving list of quests...")
                        
                        if response.status == 504:
                            retry_count += 1
                            if retry_count < max_retries:
                                delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                                logger.warning(f"{self.session_name} | Gateway Timeout while retrieving quests, retrying in {delay:.1f} sec...")
                                await asyncio.sleep(delay)
                                continue
                            else:
                                logger.error(f"{self.session_name} | Exceeded number of attempts to retrieve quests")
                                return None
                        
                        response_text = await response.text()
                        
                        if response_text.strip().startswith('<!DOCTYPE html>'):
                            retry_count += 1
                            if retry_count < max_retries:
                                delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                                logger.warning(f"{self.session_name} | Received HTML response while retrieving quests, retrying in {delay:.1f} sec...")
                                await asyncio.sleep(delay)
                                continue
                            else:
                                logger.error(f"{self.session_name} | Exceeded number of attempts to retrieve quests")
                                return None
                        
                        response.raise_for_status()
                        quests_data = json.loads(response_text)
                        
                        if quests_data.get('success') and quests_data.get('data'):
                            quests = quests_data['data']
                            logger.success(f"{self.session_name} | Found {len(quests)} quests:")
                            
                            filtered_quests = []
                            for quest in quests:
                                rewards = sum(reward['amount'] for reward in quest['rewards'])
                                progress = quest['progress']
                                status = "✅ Completed" if progress['claimed'] else "⏳ Incomplete"
                                
                                if progress['claimed']:
                                    logger.info(
                                        f"{self.session_name} | "
                                        f"Quest: {quest['title']} | "
                                        f"Reward: {rewards} | "
                                        f"Progress: {progress['current']}/{progress['total']} | "
                                        f"Status: {status}"
                                    )
                                    continue
                                
                                if quest.get('type') == 'referral' or quest.get('code') == 'referral':
                                    required_referrals = progress['total']
                                    if self.referrals_count < required_referrals:
                                        logger.info(
                                            f"{self.session_name} | "
                                            f"Quest: {quest['title']} | "
                                            f"Reward: {rewards} | "
                                            f"Progress: {self.referrals_count}/{required_referrals} | "
                                            f"Status: {status} | "
                                            f"⚠️ Skipped (insufficient referrals)"
                                        )
                                        continue
                                
                                quest_code = quest.get('code', '').lower()
                                if any(manual_type in quest_code for manual_type in manual_quests):
                                    logger.info(
                                        f"{self.session_name} | "
                                        f"Quest: {quest['title']} | "
                                        f"Reward: {rewards} | "
                                        f"Progress: {progress['current']}/{progress['total']} | "
                                        f"Status: {status} | "
                                        f"⚠️ Skipped (requires manual completion)"
                                    )
                                    continue
                                    
                                logger.info(
                                    f"{self.session_name} | "
                                    f"Quest: {quest['title']} | "
                                    f"Reward: {rewards} | "
                                    f"Progress: {progress['current']}/{progress['total']} | "
                                    f"Status: {status} | "
                                    f"✅ Added to queue"
                                )
                                filtered_quests.append(quest)
                            
                            return filtered_quests
                        return None
                    
            except asyncio.TimeoutError as error:
                retry_count += 1
                if retry_count < max_retries:
                    delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                    logger.warning(f"{self.session_name} | Timeout while retrieving quests: {str(error)}, retrying in {delay:.1f} sec...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{self.session_name} | Exceeded timeout while retrieving quests: {str(error)}")
                    return None
            except ClientResponseError as error:
                retry_count += 1
                if retry_count < max_retries:
                    delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                    logger.warning(f"{self.session_name} | HTTP Error {error.status} while retrieving quests: {error.message}, retrying in {delay:.1f} sec...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{self.session_name} | Error retrieving quests: {error.status} - {error.message}")
                    return None
            except json.JSONDecodeError as error:
                retry_count += 1
                if retry_count < max_retries:
                    delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                    logger.warning(f"{self.session_name} | JSON parsing error: {str(error)}, retrying in {delay:.1f} sec...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{self.session_name} | Response JSON parsing error: {str(error)}")
                    return None
            except Exception as error:
                retry_count += 1
                if retry_count < max_retries:
                    delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                    logger.warning(f"{self.session_name} | Error while retrieving quests: {str(error)}, retrying in {delay:.1f} sec...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{self.session_name} | Error retrieving quests: {str(error)}")
                    return None

    async def join_telegram_channel(self, channel_url: str) -> bool:
        """Joining a Telegram channel with additional actions"""
        was_connected = self.tg_client.is_connected
        
        try:
            logger.info(f"{self.session_name} | Processing Telegram channel: {channel_url}")
            
            channel_username = channel_url.split('/')[-1].strip()
            if not channel_username:
                logger.error(f"{self.session_name} | Invalid channel link: {channel_url}")
                return False

            if not was_connected:
                logger.info(f"{self.session_name} | Connecting to Telegram...")
                await self.tg_client.connect()

            try:
                channel = await self.tg_client.get_chat(channel_username)
                logger.info(f"{self.session_name} | Found channel: {channel.title} ({channel.id})")
            except UsernameNotOccupied:
                logger.error(f"{self.session_name} | Channel {channel_username} does not exist")
                return False
            except ChannelPrivate:
                logger.error(f"{self.session_name} | Channel {channel_username} is private")
                return False
            except RPCError as e:
                logger.error(f"{self.session_name} | Telegram API error while fetching channel info: {str(e)}")
                return False

            try:
                member = await self.tg_client.get_chat_member(channel.id, "me")
                if member and member.status not in ["left", "banned", "restricted"]:
                    logger.info(f"{self.session_name} | Already subscribed to channel {channel.title}")
                    await self._mute_and_archive_channel(channel)
                    return True
            except UserNotParticipant:
                logger.info(f"{self.session_name} | Not a participant of channel {channel.title}")
            except RPCError as e:
                logger.warning(f"{self.session_name} | Error checking membership: {str(e)}")

            try:
                await self.tg_client.join_chat(channel_username)
                logger.success(f"{self.session_name} | Successfully subscribed to channel {channel.title}")
                await self._mute_and_archive_channel(channel)
                return True
            except FloodWait as e:
                logger.warning(f"{self.session_name} | Flood wait of {e.value} seconds while subscribing to channel")
                await asyncio.sleep(e.value)
                return await self.join_telegram_channel(channel_url)
            except UserBannedInChannel:
                logger.error(f"{self.session_name} | Account is banned in channel {channel.title}")
                return False
            except RPCError as e:
                logger.error(f"{self.session_name} | Error subscribing to channel: {str(e)}")
                return False

        except Exception as e:
            logger.error(f"{self.session_name} | Unexpected error while processing channel {channel_username}: {str(e)}")
            return False
        finally:
            if not was_connected and self.tg_client.is_connected:
                await self.tg_client.disconnect()

    async def _mute_and_archive_channel(self, channel) -> None:
        """Helper method to mute notifications and archive the channel"""
        try:
            await self.tg_client.invoke(
                raw.functions.account.UpdateNotifySettings(
                    peer=raw.types.InputNotifyPeer(
                        peer=await self.tg_client.resolve_peer(channel.id)
                    ),
                    settings=raw.types.InputPeerNotifySettings(
                        mute_until=2147483647
                    )
                )
            )
            logger.info(f"{self.session_name} | Notifications muted for channel {channel.title}")
        except RPCError as e:
            logger.warning(f"{self.session_name} | Failed to mute notifications: {str(e)}")

        try:
            await self.tg_client.invoke(
                raw.functions.folders.EditPeerFolders(
                    folder_peers=[
                        raw.types.InputFolderPeer(
                            peer=await self.tg_client.resolve_peer(channel.id),
                            folder_id=1
                        )
                    ]
                )
            )
            logger.info(f"{self.session_name} | Channel {channel.title} added to archive")
        except RPCError as e:
            logger.warning(f"{self.session_name} | Failed to add to archive: {str(e)}")

    async def complete_quest(self, quest_id: str, quest_info: dict):
        """Completing a quest"""
        if not self.token:
            return False
            
        url = 'https://api.paws.community/v1/quests/completed'
        headers = self.get_headers(with_auth=True)
        data = json.dumps({'questId': quest_id})

        quest_title = quest_info.get('title', 'Unknown quest')
        quest_type = quest_info.get('type', 'Unknown type')
        quest_rewards = sum(reward['amount'] for reward in quest_info.get('rewards', []))
        quest_action = quest_info.get('action', 'Unknown action')
        quest_data = quest_info.get('data', '')

        logger.info(
            f"{self.session_name} | "
            f"Attempting to complete quest: {quest_title} | "
            f"Type: {quest_type} | "
            f"Action: {quest_action} | "
            f"Reward: {quest_rewards}"
        )

        if quest_type == 'social' and quest_action == 'link' and 't.me/' in quest_data:
            logger.info(f"{self.session_name} | Detected quest to subscribe to Telegram channel")
            if not await self.join_telegram_channel(quest_data):
                logger.error(f"{self.session_name} | Failed to subscribe to channel {quest_data}")
                return False
            await asyncio.sleep(5)

        retry_count = 0
        max_retries = settings.MAX_RETRIES
        
        while retry_count < max_retries:
            try:
                async with ClientSession() as session:
                    timeout = random.uniform(settings.REQUEST_TIMEOUT[0], settings.REQUEST_TIMEOUT[1])
                    async with session.post(
                        url=url,
                        headers=headers,
                        data=data,
                        ssl=False,
                        timeout=ClientTimeout(total=timeout)
                    ) as response:
                        logger.info(f"{self.session_name} | Quest '{quest_title}' completion status: {response.status}")
                        
                        if response.status == 504:
                            retry_count += 1
                            if retry_count < max_retries:
                                delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                                logger.warning(f"{self.session_name} | Gateway Timeout for quest '{quest_title}', retrying in {delay:.1f} sec...")
                                await asyncio.sleep(delay)
                                continue
                            else:
                                logger.error(f"{self.session_name} | Exceeded number of attempts to complete quest '{quest_title}'")
                                return False
                        
                        response_text = await response.text()
                        
                        if response_text.strip().startswith('<!DOCTYPE html>'):
                            retry_count += 1
                            if retry_count < max_retries:
                                delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                                logger.warning(f"{self.session_name} | Received HTML response for quest '{quest_title}', retrying in {delay:.1f} sec...")
                                await asyncio.sleep(delay)
                                continue
                            else:
                                logger.error(f"{self.session_name} | Exceeded number of attempts to complete quest '{quest_title}'")
                                return False
                        
                        try:
                            result = json.loads(response_text)
                            logger.debug(f"{self.session_name} | Server response: {response_text[:200]}...", "response")
                            
                            if result.get('success') is True:
                                logger.success(f"{self.session_name} | Quest '{quest_title}' successfully completed")
                                return await self.claim_quest(quest_id, quest_title, quest_rewards)
                            else:
                                error_message = result.get('message', 'Unknown error')
                                logger.error(f"{self.session_name} | Failed to complete quest '{quest_title}': {error_message}")
                                return False
                                
                        except json.JSONDecodeError:
                            logger.error(f"{self.session_name} | Received invalid JSON response: {response_text[:200]}")
                            return False
                        
            except Exception as error:
                retry_count += 1
                if retry_count < max_retries:
                    delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                    logger.warning(f"{self.session_name} | Error completing quest '{quest_title}': {str(error)}, retrying in {delay:.1f} sec...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{self.session_name} | Error completing quest '{quest_title}': {str(error)}")
                    return False

    async def claim_quest(self, quest_id: str, quest_title: str, quest_rewards: int):
        """Claiming reward for a quest"""
        url = 'https://api.paws.community/v1/quests/claim'
        headers = self.get_headers(with_auth=True)
        data = json.dumps({'questId': quest_id})

        retry_count = 0
        max_retries = settings.MAX_RETRIES

        while retry_count < max_retries:
            try:
                logger.info(f"{self.session_name} | Attempting to claim reward for quest '{quest_title}'")
                async with ClientSession() as session:
                    timeout = random.uniform(settings.REQUEST_TIMEOUT[0], settings.REQUEST_TIMEOUT[1])
                    async with session.post(
                        url=url,
                        headers=headers,
                        data=data,
                        ssl=False,
                        timeout=ClientTimeout(total=timeout)
                    ) as response:
                        logger.info(f"{self.session_name} | Reward claim status: {response.status}")

                        if response.status == 504:
                            retry_count += 1
                            if retry_count < max_retries:
                                delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                                logger.warning(f"{self.session_name} | Gateway Timeout while claiming reward for quest '{quest_title}', retrying in {delay:.1f} sec...")
                                await asyncio.sleep(delay)
                                continue
                            else:
                                logger.error(f"{self.session_name} | Exceeded number of attempts to claim reward for quest '{quest_title}'")
                                return False

                        response_text = await response.text()

                        if response_text.strip().startswith('<!DOCTYPE html>'):
                            retry_count += 1
                            if retry_count < max_retries:
                                delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                                logger.warning(f"{self.session_name} | Received HTML response while claiming reward for quest '{quest_title}', retrying in {delay:.1f} sec...")
                                await asyncio.sleep(delay)
                                continue
                            else:
                                logger.error(f"{self.session_name} | Exceeded number of attempts to claim reward for quest '{quest_title}'")
                                return False

                        try:
                            response.raise_for_status()
                            result = json.loads(response_text)
                            
                            if result.get('success') is True:
                                logger.success(
                                    f"{self.session_name} | "
                                    f"Received reward {quest_rewards} for quest '{quest_title}'"
                                )
                                return True
                            else:
                                error_message = result.get('message', 'Unknown error')
                                logger.error(f"{self.session_name} | Failed to claim reward for quest '{quest_title}': {error_message}")
                                return False

                        except json.JSONDecodeError:
                            logger.error(f"{self.session_name} | Received invalid JSON response while claiming reward: {response_text[:200]}")
                            return False

            except ClientResponseError as error:
                retry_count += 1
                if retry_count < max_retries:
                    delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                    logger.warning(f"{self.session_name} | HTTP Error {error.status} while claiming reward, retrying in {delay:.1f} sec...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{self.session_name} | Error claiming reward for quest '{quest_title}': {error}")
                    return False
            except Exception as error:
                retry_count += 1
                if retry_count < max_retries:
                    delay = random.uniform(settings.RETRY_DELAY[0], settings.RETRY_DELAY[1])
                    logger.warning(f"{self.session_name} | Error claiming reward: {str(error)}, retrying in {delay:.1f} sec...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{self.session_name} | Error claiming reward for quest '{quest_title}': {str(error)}")
                    return False

    async def get_user_info(self):
        if not self.token:
            return None
            
        url = 'https://api.paws.community/v1/user'
        headers = self.get_headers(with_auth=True)

        try:
            async with ClientSession(timeout=ClientTimeout(total=20)) as session:
                async with session.get(url=url, headers=headers, ssl=False) as response:
                    response.raise_for_status()
                    return await response.json()
        except Exception as error:
            logger.error(f"{self.session_name} | Error retrieving user information: {error}")
            return None

    async def check_server_availability(self) -> bool:
        """Checking server availability"""
        url = 'https://api.paws.community/v1/health'
        try:
            async with ClientSession() as session:
                async with session.get(
                    url=url,
                    timeout=ClientTimeout(total=5),
                    ssl=False
                ) as response:
                    if response.status == 200:
                        return True
                    logger.warning(f"The server returned status {response.status}")
                    return False
        except Exception as e:
            logger.error(f"Error checking server availability: {str(e)}")
            return False

    async def get_balance(self) -> int:
        """Retrieving current balance"""
        url = 'https://api.paws.community/v1/user'
        headers = self.get_headers(with_auth=True)
        
        retry_count = 0
        max_retries = settings.MAX_RETRIES
        
        while retry_count < max_retries:
            try:
                async with ClientSession() as session:
                    timeout = random.uniform(
                        settings.REQUEST_TIMEOUT[0], 
                        settings.REQUEST_TIMEOUT[1]
                    )
                    async with session.get(
                        url=url,
                        headers=headers,
                        ssl=False,
                        timeout=ClientTimeout(total=timeout)
                    ) as response:
                        logger.info(f"{self.session_name} | Balance retrieval status: {response.status}")
                        
                        if response.status == 504:
                            retry_count += 1
                            if retry_count < max_retries:
                                delay = random.uniform(
                                    settings.RETRY_DELAY[0], 
                                    settings.RETRY_DELAY[1]
                                )
                                logger.warning(f"{self.session_name} | Gateway Timeout while retrieving balance, retrying in {delay:.1f} sec...")
                                await asyncio.sleep(delay)
                                continue
                            else:
                                logger.error(f"{self.session_name} | Exceeded number of attempts to retrieve balance")
                                return 0
                        
                        response_text = await response.text()
                        
                        if response_text.strip().startswith('<!DOCTYPE html>'):
                            retry_count += 1
                            if retry_count < max_retries:
                                delay = random.uniform(
                                    settings.RETRY_DELAY[0], 
                                    settings.RETRY_DELAY[1]
                                )
                                logger.warning(f"{self.session_name} | Received HTML response while retrieving balance, retrying in {delay:.1f} sec...")
                                await asyncio.sleep(delay)
                                continue
                            else:
                                logger.error(f"{self.session_name} | Exceeded number of attempts to retrieve balance")
                                return 0
                        
                        response.raise_for_status()
                        user_data = json.loads(response_text)
                        if user_data.get('success') and user_data.get('data'):
                            balance = user_data['data'].get('gameData', {}).get('balance', 0)
                            logger.info(f"{self.session_name} | Current balance: {balance}")
                            return balance
                        return 0
                    
            except ClientResponseError as error:
                retry_count += 1
                if retry_count < max_retries:
                    delay = random.uniform(
                        settings.RETRY_DELAY[0], 
                        settings.RETRY_DELAY[1]
                    )
                    logger.warning(f"{self.session_name} | HTTP Error {error.status} while retrieving balance, retrying in {delay:.1f} sec...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{self.session_name} | Error retrieving balance: {error}")
                    return 0
            except Exception as error:
                retry_count += 1
                if retry_count < max_retries:
                    delay = random.uniform(
                        settings.RETRY_DELAY[0], 
                        settings.RETRY_DELAY[1]
                    )
                    logger.warning(f"{self.session_name} | Unexpected error while retrieving balance, retrying in {delay:.1f} sec...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"{self.session_name} | Error retrieving balance: {error}")
                    return 0

async def run_tappers(tg_clients: list[Client], proxies: list[str | None]):
    while True:
        tapper = Tapper(tg_clients[0])
        server_check_attempts = 0
        
        while server_check_attempts < settings.MAX_SERVER_CHECK_ATTEMPTS:
            if await tapper.check_server_availability():
                logger.success("🟢 Server is available, starting session processing")
                break
            
            server_check_attempts += 1
            if server_check_attempts >= settings.MAX_SERVER_CHECK_ATTEMPTS:
                delay = random.uniform(
                    settings.SLEEP_ON_SERVER_ERROR[0],
                    settings.SLEEP_ON_SERVER_ERROR[1]
                )
                logger.error(f"🔌 Server unavailable after several attempts, waiting {delay:.1f} sec...")
                await asyncio.sleep(delay)
                continue
            
            delay = random.uniform(
                settings.SERVER_CHECK_RETRY_DELAY[0],
                settings.SERVER_CHECK_RETRY_DELAY[1]
            )
            logger.warning(f"🔌 Server unavailable, attempt {server_check_attempts}/{settings.MAX_SERVER_CHECK_ATTEMPTS}, waiting {delay:.1f} sec...")
            await asyncio.sleep(delay)
        
        if server_check_attempts >= settings.MAX_SERVER_CHECK_ATTEMPTS:
            continue
        
        try:
            for client, proxy in zip(tg_clients, proxies):
                tapper = Tapper(client)
                try:
                    logger.info(f"{'='*50}")
                    logger.info(f"Processing session: {tapper.session_name}")
                    
                    if not await tapper.check_server_availability():
                        delay = random.uniform(
                            settings.SLEEP_ON_SERVER_ERROR[0],
                            settings.SLEEP_ON_SERVER_ERROR[1]
                        )
                        logger.error(f"🔌 Server became unavailable during session processing")
                        logger.info(f"⏳ Skipping remaining sessions and waiting {delay:.1f} seconds...")
                        await asyncio.sleep(delay)
                        break

                    tg_web_data = await tapper.get_tg_web_data(proxy)
                    if not tg_web_data or not await tapper.authorize(tg_web_data):
                        logger.error(f"{tapper.session_name} | Authorization error, skipping session")
                        continue

                    initial_balance = await tapper.get_balance()
                    logger.info(f"{tapper.session_name} | Initial balance: {initial_balance}")

                    completed_quests = 0
                    total_rewards = 0
                    
                    quests = await tapper.get_quests()
                    if quests:
                        for quest in quests:
                            if not quest['progress']['claimed']:
                                quest_reward = sum(reward['amount'] for reward in quest['rewards'])
                                if await tapper.complete_quest(quest['_id'], quest):
                                    completed_quests += 1
                                    total_rewards += quest_reward
                                    delay = random.uniform(
                                        settings.MIN_DELAY_BETWEEN_QUESTS,
                                        settings.MAX_DELAY_BETWEEN_QUESTS
                                    )
                                    logger.info(f"{tapper.session_name} | Waiting {delay:.1f} sec...")
                                    await asyncio.sleep(delay)

                    final_balance = await tapper.get_balance()
                    
                    logger.info(f"\n{tapper.session_name} | Session summary:")
                    logger.info(f"├── Quests completed: {completed_quests}")
                    logger.info(f"├── Rewards received: {total_rewards}")
                    logger.info(f"├── Initial balance: {initial_balance}")
                    logger.info(f"├── Final balance: {final_balance}")
                    logger.info(f"└── Increase: {final_balance - initial_balance}")
                    logger.info(f"{'='*50}\n")

                except Exception as e:
                    logger.error(f"{tapper.session_name} | Unexpected error: {e}")
                finally:
                    logger.info(f"Session processing completed: {tapper.session_name}")
                    logger.info(f"{'='*50}\n")
            
            if await tapper.check_server_availability():
                delay = random.uniform(
                    settings.SLEEP_AFTER_SESSIONS[0],
                    settings.SLEEP_AFTER_SESSIONS[1]
                )
                logger.info(f"🔄 All sessions processed, waiting {delay:.1f} sec...")
                await asyncio.sleep(delay)
            
        except Exception as e:
            delay = random.uniform(
                settings.SLEEP_ON_SERVER_ERROR[0],
                settings.SLEEP_ON_SERVER_ERROR[1]
            )
            logger.error(f"Critical error during session processing: {e}")
            logger.info(f"⏳ Waiting {delay:.1f} sec before retrying...")
            await asyncio.sleep(delay)

async def run_tapper(tg_client: Client, proxy: str | None):
    await run_tappers([tg_client], [proxy])
