from .session import Session
from .torrent_info import TorrentInfo
from .downloader import Downloader
import libtorrent as lt
import math


class TelegramNotifier:
    def __init__(self, telethon_client):
        self.client = telethon_client

    async def send_message(self, chat_id, message):
        try:
            await self.client.send_message(chat_id, message)
        except Exception as e:
            print("Error sending message to Telegram:", e)

    async def edit_message(self, message, new_text):
        try:
            await message.edit(new_text)
        except Exception as e:
            print("Error editing message on Telegram:", e)


class TorrentDownloader:
    def __init__(self, file_path, save_path, telethon_client, xx, port=6881):
        self._file_path = file_path
        self._save_path = save_path
        self._port = port  # Default port is 6881
        self._downloader = None
        self._torrent_info = None
        self._lt = lt
        self._file = None
        self._add_torrent_params = None
        self._session = Session(self._lt, port=self._port)  # Pass port to Session
        self._telegram_notifier = TelegramNotifier(telethon_client)  # Create TelegramNotifier
        self.xx = xx

    async def start_download(self, download_speed=0, upload_speed=0, chat_id=None):
        if chat_id is None:
            raise ValueError("Chat ID must be provided.")

        if self._file_path.startswith('magnet:'):
            self._add_torrent_params = self._lt.parse_magnet_uri(self._file_path)
            self._add_torrent_params.save_path = self._save_path
            self._downloader = Downloader(
                session=self._session(), torrent_info=self._add_torrent_params, 
                save_path=self._save_path, libtorrent=lt, is_magnet=True,
                progress_callback=lambda status: self._progress_callback(status, chat_id),
                telegram_notifier=self._telegram_notifier
            )

        else:
            self._torrent_info = TorrentInfo(self._file_path, self._lt)
            self._downloader = Downloader(
                session=self._session(), torrent_info=self._torrent_info(), 
                save_path=self._save_path, libtorrent=None, is_magnet=False,
                progress_callback=lambda status: self._progress_callback(status, chat_id),
                telegram_notifier=self._telegram_notifier
            )

        self._session.set_download_limit(download_speed)
        self._session.set_upload_limit(upload_speed)

        self._file = self._downloader

        self.xx = await self._telegram_notifier.send_message(chat_id, "Getting data from magnet...")
        
        await self._file.download()

    async def _progress_callback(self, status, chat_id):
        _percentage = status.progress * 100
        _download_speed = status.download_rate / 1000
        _upload_speed = status.upload_rate / 1000

        counting = math.ceil(_percentage / 5)
        visual_loading = '#' * counting + ' ' * (20 - counting)
        message = "\r\033[42m %.1f Kb/s \033[0m|\033[46m up: %.1f Kb/s \033[0m| status: %s | peers: %d  \033[96m|%s|\033[0m %d%%" % (
            _download_speed, _upload_speed, status.state, status.num_peers, visual_loading, _percentage)

        # Print to stdout
        print(message, end='')

        # Edit the existing message on Telegram
        await self._telegram_notifier.edit_message(self.xx, message)

    def pause_download(self):
        if self._downloader:
            self._downloader.pause()

    def resume_download(self):
        if self._downloader:
            self._downloader.resume()

    def stop_download(self):
        if self._downloader:
            self._downloader.stop()

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def __call__(self):
        pass
