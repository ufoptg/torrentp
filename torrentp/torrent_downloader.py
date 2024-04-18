from .session import Session
from .torrent_info import TorrentInfo
from .downloader import Downloader
import libtorrent as lt


class TorrentDownloader:
    def __init__(self, file_path, save_path, progress_callback=None):
        self._file_path = file_path
        self._save_path = save_path
        self._downloader = None
        self._torrent_info = None
        self._lt = lt
        self._file = None
        self._add_torrent_params = None
        self._session = Session(self._lt)
        self.progress_callback = progress_callback

    async def start_download(self, download_speed=0, upload_speed=0):
        if self._file_path.startswith('magnet:'):
            self._add_torrent_params = self._lt.parse_magnet_uri(self._file_path)
        else:
            self._add_torrent_params = self._lt.add_torrent_params()
            self._add_torrent_params.save_path = self._save_path

        self._downloader = Downloader(session=self._session(), torrent_info=self._add_torrent_params,
                                      save_path=self._save_path, libtorrent=lt, is_magnet=True, progress_callback=self.progress_callback)

        self._session.set_download_limit(download_speed)
        self._session.set_upload_limit(upload_speed)

        self._file = self._downloader
        while not self._file.is_seeding:
            s = self._file.status()
            if self.progress_callback:
                await self.progress_callback(s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, s.num_peers, s.state)
            await asyncio.sleep(1)

        await self._file.download()

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
