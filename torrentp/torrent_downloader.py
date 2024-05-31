from .session import Session
from .torrent_info import TorrentInfo
from .downloader import Downloader
import libtorrent as lt
import math

class TelegramNotifier:
    def __init__(self, telethon_client):
        self.client = telethon_client

    async def send_message(self, chat_id, message):
        sent_message = await self.client.send_message(chat_id, message)
        return sent_message

    async def edit_message(self, chat_id, message_id, new_message):
        edited_message = await self.client.edit_message(chat_id, message_id, new_message)
        return edited_message

class TorrentDownloader:
    def __init__(self, file_path, save_path, telethon_client, event, port=6881):
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
        self._message = event

    async def start_download(self, chat_id, download_speed=0, upload_speed=0):
        if chat_id is None:
            raise ValueError("Chat ID must be provided.")

        # If self._message is None, send a new message. Otherwise, edit the existing message.
        if self._message is None:
            self._message = await self._telegram_notifier.send_message(chat_id, "Getting data from magnet...")
        else:
            await self._telegram_notifier.edit_message(chat_id, self._message.original_update.msg_id, "Getting data from magnet...")

        if not self._message:
            print("Failed to send initial message to Telegram")
            return

        if self._file_path.startswith('magnet:'):
            self._add_torrent_params = self._lt.parse_magnet_uri(self._file_path)
            self._add_torrent_params.save_path = self._save_path
            self._downloader = Downloader(
                session=self._session(), torrent_info=self._add_torrent_params, 
                save_path=self._save_path, libtorrent=lt, is_magnet=True,
                progress_callback=self._progress_callback,
                telegram_notifier=self._telegram_notifier
            )
        else:
            self._torrent_info = TorrentInfo(self._file_path, self._lt)
            self._downloader = Downloader(
                session=self._session(), torrent_info=self._torrent_info(), 
                save_path=self._save_path, libtorrent=None, is_magnet=False,
                progress_callback=self._progress_callback,
                telegram_notifier=self._telegram_notifier
            )

        self._session.set_download_limit(download_speed)
        self._session.set_upload_limit(upload_speed)

        self._file = self._downloader
        await self._file.download()

    async def _progress_callback(self, status):
        _percentage = status.progress * 100
        _download_speed = status.download_rate / 1000
        _upload_speed = status.upload_rate / 1000

        counting = math.ceil(_percentage / 5)
        visual_loading = '#' * counting + ' ' * (20 - counting)
        message = "Download speed: %.1f Kb/s | Upload speed: %.1f Kb/s | Status: %s | Peers: %d | Progress: %s | %d%%" % (
            _download_speed, _upload_speed, status.state, status.num_peers, visual_loading, _percentage)

        # Edit the Telegram message with the progress
        try:
            await self._message.edit(message)
        except Exception as e:
            print(f"Error editing message: {e}")

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
