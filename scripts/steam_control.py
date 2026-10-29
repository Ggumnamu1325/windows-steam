#!/usr/bin/env python3
"""Operate only the selected wrapper's Wine prefix; never kill by process name."""
import argparse, json, os, subprocess, sys, tempfile, time
from pathlib import Path

class Controller:
    def __init__(self, wrapper):
        self.wrapper = Path(wrapper).expanduser().resolve()
        self.contents = self.wrapper / 'Contents'
        self.prefix = self.contents / 'SharedSupport/prefix'
        self.bin = self.contents / 'SharedSupport/wine/bin'
        self.steam = self.prefix / 'drive_c/Program Files (x86)/Steam/Steam.exe'
        self.env = dict(os.environ, WINEPREFIX=str(self.prefix),
            DYLD_FALLBACK_LIBRARY_PATH=str(self.contents/'Frameworks')+':'+str(self.contents/'SharedSupport/wine/lib'))
    def validate(self):
        for p in [self.bin/'wine', self.bin/'wineserver', self.steam, self.contents/'MacOS/Sikarugir']:
            if not p.is_file(): raise RuntimeError('필요한 실행 파일이 없습니다: '+p.name)
    def run(self, executable, args, timeout=10):
        return subprocess.run([str(executable), *args], env=self.env, cwd=str(self.contents),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout, check=False)
    def wait_stopped(self, timeout):
        try: return self.run(self.bin/'wineserver', ['-w'], timeout).returncode == 0
        except subprocess.TimeoutExpired: return False
    def running(self): return not self.wait_stopped(.3)
    def clear_stale_lock(self):
        if self.running(): return
        encoded='xKWx'+str(self.wrapper).strip('/').replace('/', 'xKWx')
        lock=Path(tempfile.gettempdir())/encoded/'lockfile'
        if lock.is_file(): lock.unlink()
    def open(self):
        self.validate()
        if not self.running():
            self.clear_stale_lock()
            subprocess.Popen([str(self.contents/'MacOS/Sikarugir')], env=self.env,
                cwd=str(self.contents), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
            # The wrapper prepares rendering and DLL overrides before Steam starts.
            for _ in range(40):
                if self.running(): break
                time.sleep(.25)
            else: raise RuntimeError('Wine 실행 환경이 시작되지 않았습니다.')
        # A second invocation asks the existing Steam instance to show its library.
        try: self.run(self.bin/'wine', [str(self.steam), '-language', 'koreana', 'steam://open/games'], 12)
        except subprocess.TimeoutExpired: pass  # Steam may keep its launcher attached.
    def quit(self):
        self.validate()
        if not self.running(): return
        try: self.run(self.bin/'wine', [str(self.steam), '-shutdown'], 10)
        except subprocess.TimeoutExpired: pass
        if self.wait_stopped(20): return
        # Prefix-scoped fallback, after allowing Steam to shut down normally.
        self.run(self.bin/'wineserver', ['-k'], 10)
        if not self.wait_stopped(10): raise RuntimeError('종료되지 않은 Windows Steam 프로세스가 있습니다.')

def main():
    p=argparse.ArgumentParser();p.add_argument('action', choices=['open','quit','status']);p.add_argument('--wrapper', required=True)
    a=p.parse_args();c=Controller(a.wrapper)
    try:
        if a.action=='status': print('running' if c.running() else 'stopped')
        else: getattr(c,a.action)()
    except Exception as e: print(str(e),file=sys.stderr);return 1
    return 0
if __name__=='__main__':sys.exit(main())
