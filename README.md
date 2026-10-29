# Windows Steam

**맥에서 Windows용 Steam을 실행하고, 호환되는 Windows Steam 게임을 설치·플레이할 수 있게 하는 도구입니다.** Sikarugir·Wine을 사용하며 게임마다 호환 여부는 다를 수 있습니다.

## 설치

macOS 14.6 이상에서 터미널에 아래 명령을 붙여 넣으세요.

```sh
curl -fsSL https://raw.githubusercontent.com/Ggumnamu1325/windows-steam/main/install.sh | bash
```

기존 Windows Steam이 있으면 업데이트하고, 없으면 공식 실행 환경과 Steam 설치 파일을 자동으로 내려받아 준비합니다. 개발 도구·Rosetta 설치 승인이 나오면 안내에 따르고, Steam 설치 창의 약관 확인과 계정 로그인은 직접 진행하세요. 개발 도구 설치 후에는 같은 명령을 다시 실행하면 됩니다.

Dock에는 Windows Steam 제어 앱 하나, 상단 메뉴 막대에는 게임패드 아이콘 하나로 표시합니다.

## 켜기

응용 프로그램의 **Windows Steam**을 열고 Steam에 로그인하세요. 라이브러리에서 게임을 설치하고 실행하면 됩니다.

## 끄기

- 창의 **닫기 버튼**: 창만 닫고 Steam은 백그라운드에서 유지합니다.
- 상단 메뉴 막대의 **게임패드 아이콘 → Steam 창 열기**: 창을 다시 엽니다.
- **게임패드 아이콘 → Windows Steam 종료**: 백그라운드를 포함해 종료합니다.

메뉴 바깥을 클릭하거나 Escape를 누르면 메뉴가 닫힙니다.
