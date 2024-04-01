import sys
import time
import asyncio
import random

class Downloader:
    def __init__(self, session, torrent_info, save_path, libtorrent, is_magnet, progress_callback):
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
        self._paused = False
        self._progress_callback = progress_callback  # Added progress callback

    def status(self):
        if not self._is_magnet:
            self._file = self._session.add_torrent({'ti': self._torrent_info, 'save_path': f'{self._save_path}'})
            self._status = self._file.status()
        else:
            self._add_torrent_params = self._torrent_info
            self._add_torrent_params.save_path = self._save_path
            self._file = self._session.add_torrent(self._add_torrent_params)
            self._status = self._file.status()
        return self._status

    @property
    def name(self):
        self._name = self.status().name
        return self._name

    async def download(self):
        print(f'Start downloading {self.name}')
        initial_percentage = random.randint(3, 5)
        print_at = initial_percentage
        print('\r%.2f%% complete' % (initial_percentage), end=' ')
        sys.stdout.flush()
        while not self._status.is_seeding:
            if not self._paused:
                s = self.status()
                current_progress = s.progress * 100
                if current_progress >= print_at:
                    print('\r%.2f%% complete (down: %.1f kB/s up: %.1f kB/s peers: %d) %s' % (
                        current_progress, s.download_rate / 1000, s.upload_rate / 1000,
                        s.num_peers, s.state), end=' ')
                    sys.stdout.flush()
                    interval = random.randint(5, 8)
                    print_at += interval
                    # Call progress callback here
                    self._progress_callback(current_progress)
            await asyncio.sleep(2)

        print(self._status.name, 'downloaded successfully.')

    def pause(self):
        self._file.pause()
        self._paused = True

    def resume(self):
        self._file.resume()
        self._paused = False

    def stop(self):
        self._session.remove_torrent(self._file)
        self._file = None

    def __str__(self):
        pass

    def __repr__(self):
        pass

    def __call__(self):
        pass
