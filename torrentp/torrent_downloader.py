from .session import Session
from .torrent_info import TorrentInfo
from .downloader import Downloader
import libtorrent as lt
import asyncio
import sys
import time

class TorrentDownloader:
    def __init__(self, file_path, save_path):
        self._file_path = file_path
        self._save_path = save_path
        self._downloader = None
        self._torrent_info = None
        self._lt = lt
        self._file = None
        self._add_torrent_params = None
        self._session = Session(self._lt)

    async def start_download(self, download_speed=0, upload_speed=0, event=None):
        if self._file_path.startswith('magnet:'):
            self._add_torrent_params = self._lt.parse_magnet_uri(self._file_path)
            self._add_torrent_params.save_path = self._save_path
            self._downloader = Downloader(session=self._session(), torrent_info=self._add_torrent_params,
                                          save_path=self._save_path, libtorrent=lt, is_magnet=True)

        else:
            self._torrent_info = TorrentInfo(self._file_path, self._lt)
            self._downloader = Downloader(session=self._session(), torrent_info=self._torrent_info(),
                                          save_path=self._save_path, libtorrent=None, is_magnet=False)

        self._session.set_download_limit(download_speed)
        self._session.set_upload_limit(upload_speed)

        self._file = self._downloader
        await event.edit(f"Starting download of {self._file_path}...")
        await self._file.download(progress_callback=self.progress_callback)

    async def progress_callback(self, status, event):
        await event.edit(f"Progress: {status.progress * 100:.2f}%")

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def __call__(self):
        pass
