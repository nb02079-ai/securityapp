# 개발 환경 준비 (Windows, 작업 2-1)

## 1. 설치
1. **JDK 21** — [Eclipse Temurin (adoptium.net)](https://adoptium.net/temurin/releases/)에서 받습니다.
   - 다운로드 페이지는 기본으로 최신판(예: 25)을 보여 줍니다. **버전을 21 (LTS)로 직접 고르고** Windows x64 `.msi`를 받으세요. 25는 지금 쓰는 Gradle 8.14·Kotlin 2.2에서 돌아가지 않습니다.
   - 설치 화면의 기능 목록에서 **"Set JAVA_HOME variable"은 기본으로 꺼져 있습니다.** "로컬 하드 드라이브에 설치"로 바꿔 켜 주세요.
   - 확인: 명령 프롬프트를 **새로 열고** 아래 세 줄이 모두 `jdk-21...`·`21`을 보여 주는지 봅니다.
     ```
     where java
     echo %JAVA_HOME%
     java -version
     ```
2. **IntelliJ IDEA** — [jetbrains.com/idea/download](https://www.jetbrains.com/idea/download/)에서 Windows `.exe`를 받습니다. 2025.3부터 Community와 Ultimate가 "IntelliJ IDEA" 하나로 합쳐져 Community 버튼이 따로 없습니다. 구독 없이 쓰는 기본 기능에 Kotlin 개발이 들어 있습니다 (처음에 켜지는 30일 유료 체험이 끝나도 그대로 쓸 수 있음).
   - "Kiro"는 JetBrains 제품이 아니니 받지 않습니다.
3. (권장) **GitHub Desktop** — 이제 코드 파일이 많아져 웹에서 하나씩 올리기 어렵습니다. GitHub Desktop으로 저장소를 내려받고(Clone), 바뀐 파일을 한 번에 올릴(Commit → Push) 수 있습니다.

Gradle은 따로 설치하지 않습니다. 저장소에 들어 있는 `gradlew.bat`이 처음 실행할 때 알맞은 버전을 내려받습니다.

## 2. 처음 실행
저장소 폴더에서 명령 프롬프트를 열고:
```
gradlew.bat test
```
- 처음에는 Gradle과 Kotlin을 내려받느라 몇 분 걸립니다.
- 끝에 `BUILD SUCCESSFUL`이 나오면 준비 끝입니다.
- 골격 실행: `gradlew.bat :eval:run` → `securityapp eval 골격 동작: OBSERVE`
- 한글이 `占쏙옙`처럼 깨지면 명령 프롬프트가 한글을 CP949로 읽는 것입니다. 먼저 `chcp 65001`을 실행하면 바르게 보입니다 (평가 결과는 UTF-8 파일로 저장하므로 영향 없음).

## 3. IntelliJ에서 열기
File → Open → 저장소 폴더 선택 → "Trust Project" → 오른쪽 아래에서 Gradle 불러오기가 끝날 때까지 기다립니다. `engine/src/test/.../SignalTest.kt`를 열고 초록 실행 버튼으로 테스트를 돌릴 수 있습니다.

## 4. 자동 테스트 (GitHub Actions)
`.github/workflows/test.yml`이 저장소에 올라가면 push할 때마다 GitHub에서 `gradlew test`가 돕니다. 저장소의 **Actions** 탭에서 결과를 볼 수 있고, 실패하면 빨간 X가 표시됩니다.

## 문제가 생기면
- `JAVA_HOME is not set` → JDK 설치 때 JAVA_HOME 옵션을 켜지 않은 경우.
- `JAVA_HOME is set to an invalid directory` → 예전에 넣은 JAVA_HOME이 없는 폴더를 가리키는 경우. 실제 위치(`where java`에서 `\bin\java.exe` 앞부분)로 바꿉니다:
  ```
  setx JAVA_HOME "C:\Program Files\Eclipse Adoptium\jdk-21.x.x.x-hotspot"
  ```
  새 창에서도 예전 값이 나오면 "시스템 환경 변수 편집" → "환경 변수"의 **시스템 변수** 쪽 `JAVA_HOME`도 고치거나 지웁니다.
- `Unsupported class file major version` → JDK가 21이 아닌 경우. `java -version`으로 확인합니다.
- 오류 메시지 전체를 복사해 원래 세션에 붙여 주시면 됩니다.
