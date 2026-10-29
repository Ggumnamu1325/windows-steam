#!/usr/bin/env python3
"""Download verified official dependencies into a NEW wrapper, or update an existing one."""
import argparse, hashlib, os, platform, plistlib, shutil, subprocess, sys, tarfile, tempfile, urllib.request
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parent.parent
ASSETS={
 'template':('https://github.com/Sikarugir-App/Wrapper/releases/download/v1.0/Template-1.0.21.tar.xz','bbe996e4e4375318485953d0c7818b7b4b0a4dc1f13303bcc584f99f7602f78d'),
 'engine':('https://github.com/Sikarugir-App/Engines/releases/download/v1.0/WS12WineSikarugir10.0_8.tar.xz','2a6bcf2a3bf13cddf825599b6bc1e3659cbf71e1282c6d77141a92f6ac8d4c68')}
STEAM_URL='https://cdn.cloudflare.steamstatic.com/client/installer/SteamSetup.exe'

def download(url,target,digest=None):
 target=Path(target)
 if digest and target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest()==digest:return target
 target.parent.mkdir(parents=True,exist_ok=True)
 temporary=target.with_suffix(target.suffix+'.part')
 print('다운로드: '+target.name,flush=True)
 try:
  with urllib.request.urlopen(url,timeout=60) as response,temporary.open('wb') as out:
   shutil.copyfileobj(response,out)
  if digest and hashlib.sha256(temporary.read_bytes()).hexdigest()!=digest:raise RuntimeError('공식 배포 파일의 SHA-256이 일치하지 않습니다.')
  temporary.replace(target)
 finally:
  if temporary.exists():temporary.unlink()
 return target

def unpack(archive,destination):
 """Write files before links so no archive member can traverse a created symlink."""
 destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
 if any(destination.iterdir()):raise ValueError('압축 해제 대상은 비어 있어야 합니다.')
 links=[]
 with tarfile.open(archive) as tar:
  for member in tar:
   path=PurePosixPath(member.name)
   if path.is_absolute() or '..' in path.parts:raise ValueError('잘못된 압축 경로')
   target=destination.joinpath(*path.parts)
   if member.isdir():target.mkdir(parents=True,exist_ok=True)
   elif member.isfile():
    target.parent.mkdir(parents=True,exist_ok=True)
    with tar.extractfile(member) as src,target.open('wb') as dst:shutil.copyfileobj(src,dst)
    target.chmod(member.mode&0o777)
   elif member.issym() or member.islnk():links.append((member,target))
   else:raise ValueError('지원하지 않는 압축 항목')
  for member,target in links:
   parent=target.parent.resolve()
   if parent!=destination.resolve() and destination.resolve() not in parent.parents:raise ValueError('링크 상위 경로가 압축 폴더 밖입니다.')
   target.parent.mkdir(parents=True,exist_ok=True)
   if member.issym():target.symlink_to(member.linkname)
   else:
    link=PurePosixPath(member.linkname)
    if link.is_absolute() or '..' in link.parts:raise ValueError('잘못된 하드 링크')
    os.link(destination.joinpath(*link.parts),target)

def choose_wrapper(explicit=None):
 if explicit:return Path(explicit).expanduser().resolve()
 for p in [Path('/Applications/Windows Steam.app'),Path.home()/'Applications/Windows Steam.app']:
  if p.exists():return p
 return Path.home()/'Applications/Windows Steam.app'

def wine_environment(contents):
 return dict(os.environ,WINEPREFIX=str(contents/'SharedSupport/prefix'),DYLD_FALLBACK_LIBRARY_PATH=str(contents/'Frameworks')+':'+str(contents/'SharedSupport/wine/lib'))

def prepare_new(wrapper,cache):
 if wrapper.exists():raise RuntimeError('기존 앱은 덮어쓰지 않습니다.')
 template=download(*[ASSETS['template'][0],cache/'template.tar.xz',ASSETS['template'][1]])
 engine=download(*[ASSETS['engine'][0],cache/'engine.tar.xz',ASSETS['engine'][1]])
 wrapper.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='.windows-steam-',dir=wrapper.parent) as tmp:
  tmp=Path(tmp);unpack(template,tmp/'template');unpack(engine,tmp/'engine')
  apps=list((tmp/'template').glob('*.app'))
  if len(apps)!=1:raise RuntimeError('공식 템플릿 구조를 확인할 수 없습니다.')
  app=apps[0];wine=app/'Contents/SharedSupport/wine'
  if wine.is_symlink() or wine.is_file():wine.unlink()
  elif wine.exists():shutil.rmtree(wine)
  shutil.copytree(tmp/'engine/wswine.bundle',wine,symlinks=True)
  p=app/'Contents/Info.plist';info=plistlib.loads(p.read_bytes())
  info.update({'CFBundleName':'Windows Steam','CFBundleIdentifier':'local.windowssteam.sikarugir','Program Name and Path':'/SteamSetup.exe','Program Flags':''})
  info.pop('NSBGOnly',None);p.write_bytes(plistlib.dumps(info))
  # Atomic installation in the same filesystem; no existing app or games are replaced.
  app.rename(wrapper)

def ensure_steam(wrapper,cache):
 c=wrapper/'Contents';steam=c/'SharedSupport/prefix/drive_c/Program Files (x86)/Steam/Steam.exe'
 if steam.is_file():return
 setup=download(STEAM_URL,cache/'SteamSetup.exe')
 env=wine_environment(c);wine=c/'SharedSupport/wine/bin/wine'
 prefix=c/'SharedSupport/prefix';prefix.mkdir(parents=True,exist_ok=True)
 # Let the official wrapper initialize its prefix and graphics configuration.
 (prefix/'drive_c').mkdir(parents=True,exist_ok=True);shutil.copy2(setup,prefix/'drive_c/SteamSetup.exe')
 print('공식 Steam 설치 창이 열립니다. 설치 안내와 약관은 직접 확인해 주세요.',flush=True)
 subprocess.Popen([str(c/'MacOS/Sikarugir')],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 input('Steam 설치 창에서 설치를 마친 뒤 여기에 돌아와 Enter를 누르세요: ')
 if not steam.is_file():raise RuntimeError('Steam 설치가 완료되지 않았습니다. 설치 완료 후 같은 명령을 다시 실행하세요.')
 p=c/'Info.plist';info=plistlib.loads(p.read_bytes());info['Program Name and Path']='/Program Files (x86)/Steam/Steam.exe';info['Program Flags']='-language koreana steam://open/games';p.write_bytes(plistlib.dumps(info))

def main():
 p=argparse.ArgumentParser();p.add_argument('--wrapper');p.add_argument('--plan',action='store_true');a=p.parse_args()
 wrapper=choose_wrapper(a.wrapper)
 if a.plan:
  print('기존 앱 업데이트' if wrapper.exists() else '공식 실행 환경 새 설치');print(wrapper);return
 if platform.system()!='Darwin':raise SystemExit('macOS 전용입니다.')
 version=tuple(int(x) for x in platform.mac_ver()[0].split('.')[:2])
 if version<(14,6):raise SystemExit('macOS 14.6 이상이 필요합니다.')
 if platform.machine()=='arm64':
  translated=subprocess.run(['/usr/bin/arch','-x86_64','/usr/bin/true'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
  if not translated:
   print('Rosetta 설치가 필요합니다. Apple 약관을 직접 확인해 주세요.',flush=True)
   subprocess.run(['/usr/sbin/softwareupdate','--install-rosetta'],check=True)
 cache=Path.home()/'Library/Caches/windows-steam-installer'
 if not wrapper.exists():prepare_new(wrapper,cache)
 if not (wrapper/'Contents/MacOS/Sikarugir').is_file():raise SystemExit('지원하는 Sikarugir 앱이 아닙니다. 기존 앱은 변경하지 않았습니다.')
 ensure_steam(wrapper,cache)
 # Ask before stopping an existing session, so an active game is never silently killed.
 status=subprocess.run([sys.executable,str(ROOT/'scripts/steam_control.py'),'status','--wrapper',str(wrapper)],capture_output=True,text=True,check=True)
 if status.stdout.strip()=='running':
  reply=input('Windows Steam이 실행 중입니다. 게임을 저장하고 종료한 뒤 업데이트하려면 y를 입력하세요: ')
  if reply.strip().lower()!='y':raise SystemExit('설치를 취소했습니다. 기존 앱과 게임은 그대로입니다.')
 subprocess.run([sys.executable,str(ROOT/'scripts/steam_control.py'),'quit','--wrapper',str(wrapper)],check=True)
 subprocess.run([sys.executable,str(ROOT/'scripts/install.py'),'--wrapper',str(wrapper)],check=True)
 print('설치 완료: '+str(wrapper)+'\n앱을 열고 Steam에 로그인하세요.',flush=True)
if __name__=='__main__':main()
