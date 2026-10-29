# Windows Steam

macOS의 기존 Sikarugir·Wine Steam 래퍼에 실행·종료 제어와 기본 메뉴 막대를 추가하는 소스 프로젝트입니다.

## 동작

- 앱을 실행하거나 다시 열면 Steam 라이브러리 창을 요청합니다.
- Steam 창의 닫기 버튼은 Steam 자체의 백그라운드 동작을 유지합니다.
- macOS 메뉴 막대의 게임패드 아이콘에서 창을 다시 열거나 완전히 종료할 수 있습니다.
- 메뉴는 기본 NSMenu를 사용하므로 바깥 클릭과 Escape로 닫힙니다.
- 종료는 Steam 정상 종료 요청을 먼저 보내고, 남은 프로세스가 있으면 해당 Wine prefix만 종료합니다.

## 준비

macOS 14.6 이상, Xcode Command Line Tools(Swift 컴파일러와 Python 3), 사용자가 직접 설치한 Sikarugir 래퍼와 Windows Steam이 필요합니다. Apple Silicon에서는 기존 Wine 엔진의 Rosetta 요구사항도 충족해야 합니다.

Sikarugir는 [공식 프로젝트](https://github.com/Sikarugir-App/Sikarugir)에서 설치하세요. Steam은 Valve 공식 설치 파일을 사용해 본인 계정으로 설치합니다. 이 저장소에는 외부 런타임이나 Steam을 재배포하지 않습니다.

## 빌드와 설치

```sh
python3 scripts/install.py --build-only
python3 -m unittest discover -s tests
# 기존 래퍼를 종료하고 개인 백업을 만든 뒤 설치합니다.
python3 scripts/install.py --wrapper "/Applications/Windows Steam.app"
```

설치는 기존 앱에 새 런처와 메뉴 도우미를 추가하고 실행 진입점을 변경합니다. 게임·계정·Wine prefix는 복사하거나 삭제하지 않습니다. 모든 설치 경로는 지정한 래퍼에서 계산하며 개인 사용자 경로는 소스에 포함하지 않습니다.

## 구성

- `Sources/Launcher.swift`: 기존 앱에서 메뉴 도우미를 여는 진입점
- `Sources/MenuApp.swift`: 네이티브 메뉴와 재실행·종료 제어
- `scripts/steam_control.py`: 해당 prefix의 실행·종료 처리
- `scripts/install.py`: 로컬 빌드와 기존 래퍼에 통합
- `tests/`: 중복 실행, 정상·비정상 종료와 prefix 격리 검증

공개 대상은 위 소스·테스트·문서뿐입니다. 게임, 사용자 설정, 저장 파일, 로그, 토큰, Wine prefix, Steam 설치 파일, 배포용 엔진과 원본 앱 전체는 포함하지 않습니다. 공개 소스의 빌드 검증과 실제 게임 호환성은 별개입니다.
