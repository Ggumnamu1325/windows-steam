#!/usr/bin/env python3
"""Build and integrate into an existing user-owned wrapper; never bundle its data."""
import argparse,plistlib,shutil,subprocess,os,time,signal
from presentation_config import configure
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--wrapper',default='/Applications/Windows Steam.app');p.add_argument('--build-only',action='store_true');a=p.parse_args()
root=Path(__file__).resolve().parent.parent;build=root/'.build';build.mkdir(exist_ok=True)
for source,target in [('MenuApp.swift','WindowsSteamMenu'),('Launcher.swift','WindowsSteamLauncher')]:
 subprocess.run(['xcrun','swiftc','-swift-version','5','-O','-framework','AppKit',str(root/'Sources'/source),'-o',str(build/target)],check=True)
subprocess.run(['xcrun','clang','-arch','arm64','-arch','x86_64','-mmacosx-version-min=14.6','-fobjc-arc','-dynamiclib','-framework','AppKit',str(root/'Sources/WinePresentation.m'),'-o',str(build/'WindowsSteamPresentation.dylib')],check=True)
if a.build_only:raise SystemExit()
c=Path(a.wrapper).expanduser().resolve()/'Contents'
if not (c/'MacOS/Sikarugir').is_file():raise SystemExit('Select an existing Sikarugir wrapper.')
# An already-running helper would keep the old UI even after replacing its file.
helper_executable=c/'Resources/Windows Steam Menu.app/Contents/MacOS/WindowsSteamMenu'
def helper_pids():
 result=subprocess.check_output(['/bin/ps','-axo','pid=,comm='],text=True)
 return [int(line.strip().split(None,1)[0]) for line in result.splitlines()
         if len(line.strip().split(None,1))==2 and line.strip().split(None,1)[1]==str(helper_executable)]
if helper_executable.exists() and helper_pids():
 # This affects only the exact helper inside the selected wrapper.
 for pid in helper_pids():
  try:os.kill(pid,signal.SIGTERM)
  except ProcessLookupError:pass
 for _ in range(30):
  if not helper_pids():break
  time.sleep(.1)
 else:raise SystemExit('Close the selected Windows Steam menu helper before updating.')
helper=c/'Resources/Windows Steam Menu.app/Contents';(helper/'MacOS').mkdir(parents=True,exist_ok=True);(helper/'Resources').mkdir(exist_ok=True)
shutil.copy2(build/'WindowsSteamMenu',helper/'MacOS/WindowsSteamMenu')
shutil.copy2(root/'scripts/steam_control.py',helper/'Resources/steam_control.py')
(helper/'Info.plist').write_bytes(plistlib.dumps({'CFBundleIdentifier':'local.windowssteam.menu','CFBundleName':'Windows Steam','CFBundleExecutable':'WindowsSteamMenu','CFBundlePackageType':'APPL','CFBundleVersion':'1','LSUIElement':False,'LSMinimumSystemVersion':'14.6'}))
subprocess.run(['codesign','--force','--sign','-',str(helper.parent)],check=True)
shutil.copy2(build/'WindowsSteamPresentation.dylib',c/'Resources/WindowsSteamPresentation.dylib')
subprocess.run(['codesign','--force','--sign','-',str(c/'Resources/WindowsSteamPresentation.dylib')],check=True)
shutil.copy2(build/'WindowsSteamLauncher',c/'MacOS/WindowsSteamLauncher')
subprocess.run(['codesign','--force','--sign','-',str(c/'MacOS/WindowsSteamLauncher')],check=True)
p=c/'Info.plist'
data=configure(plistlib.loads(p.read_bytes()), c/'Resources/WindowsSteamPresentation.dylib')
p.write_bytes(plistlib.dumps(data))


# Route the wrapper's own Quit command through the same native controller.
quit_script=c/'Resources/Scripts/QuitScript'
quit_script.write_text('#!/bin/sh\nCONTENTS="$(cd "$(dirname "$0")/../.." && pwd)"\nexec "$CONTENTS/Resources/Windows Steam Menu.app/Contents/MacOS/WindowsSteamMenu" --quit\n')
quit_script.chmod(0o755)
# Replace Wine's sticky tray popup with the native NSStatusItem menu.
env=dict(os.environ,WINEPREFIX=str(c/'SharedSupport/prefix'),DYLD_FALLBACK_LIBRARY_PATH=str(c/'Frameworks')+':'+str(c/'SharedSupport/wine/lib'))
subprocess.run([str(c/'SharedSupport/wine/bin/wine'),'reg','add',r'HKCU\Software\Wine\Explorer','/v','ShowSystray','/t','REG_DWORD','/d','0','/f'],env=env,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=30)
subprocess.run([str(c/'SharedSupport/wine/bin/wineserver'),'-k'],env=env,check=True,timeout=10)
subprocess.run([str(c/'SharedSupport/wine/bin/wineserver'),'-w'],env=env,check=True,timeout=10)

register='/System/Library/Frameworks/CoreServices.framework/Frameworks/LaunchServices.framework/Support/lsregister'
subprocess.run([register,'-f',str(helper.parent)],check=True)
subprocess.run([register,'-f',str(c.parent)],check=True)

print('Installed native menu controller. Runtime, games and account data were not copied or deleted.')
