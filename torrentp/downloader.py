import sys
import asyncio
import math
import time


class Downloader:
    def __init__(self, session, torrent_info, save_path, libtorrent, is_magnet, progress_callback, telegram_notifier):
        self._session = session
        self._torrent_info = torrent_info
        self._save_path = save_path
        self._file = None
        self._status = None
        self._name = ''
        self._state = ''
        self._lt = libtorrent
        self._add_torrent_params = None
        self._is_magnet = is_magnet
        self._progress_callback = progress_callback
        self._telegram_notifier = telegram_notifier
        self._paused = False

    def status(self):
        if not self._is_magnet:
            self._file = self._session.add_torrent({'ti': self._torrent_info, 'save_path': f'{self._save_path}'})
            self._status = self._file.status()
        else:
            self._add_torrent_params = self._torrent_info
            self._add_torrent_params.save_path = self._save_path
            self._file = self._session.add_torrent(self._add_torrent_params)
            self._status = self._file.status()
            while(not self._file.has_metadata()):
                time.sleep(1)
        return self._status

    @property
    def name(self):
        self._name = self.status().name
        return self._name

    async def download(self):
        self.get_size_info(self.status().total_wanted)

        while not self._status.is_seeding:
            if not self._paused:
                await self._progress_callback(self.status())
                sys.stdout.flush()

            await asyncio.sleep(1)
        print('\033[92m' +  "\nDownloaded successfully." + '\033[0m')

    def get_size_info(self, byte_length):
        if not self._is_magnet:
            _file_size = byte_length / 1000
            _size_info = 'Size: %.2f ' % _file_size
            _size_info += 'MB' if _file_size > 1000 else 'KB'
            print('\033[95m' + _size_info  + '\033[0m')

        if self.status().name:
            print('\033[95m' + f'Saving as: {self.status().name}' + '\033[0m')

    def pause(self):
        print("Pausing download...")
        if self._file:
            self._file.pause()
            self._paused = True
            print("Download paused successfully.")
        else:
            print("Download file instance not found.")

    def resume(self):
        print("Resuming download...")
        if self._file:
            if self._paused:
                self._file.resume()
                self._paused = False
                print("Download resumed successfully.")
            else:
                print("Download is not paused. No action taken.")
        else:
            print("Download file instance not found.")

    def stop(self):
        print("Stopping download...")
        if self._file:
            self._session.remove_torrent(self._file)
            self._file = None
            print("Download stopped successfully.")
        else:
            print("Download file instance not found.")

    def is_paused(self):
        return self._paused

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def __call__(self):
        pass

