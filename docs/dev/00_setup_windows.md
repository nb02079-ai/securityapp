# 개발 환경 준비 (Windows, 작업 2-1)

## 1. 설치
1. **JDK 21** — [Eclipse Temurin 21 (adoptium.net)](https://adoptium.net/)에서 Windows x64 `.msi`를 받아 설치합니다. 설치 화면의 "Set JAVA_HOME variable"을 켜 주세요.
   - 확인: 명령 프롬프트를 새로 열고 `java -version` → `openjdk version "21..."`
2. **IntelliJ IDEA Community Edition** (무료) — JetBrains 사이트에서 설치합니다.
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

## 3. IntelliJ에서 열기
File → Open → 저장소 폴더 선택 → "Trust Project" → 오른쪽 아래에서 Gradle 불러오기가 끝날 때까지 기다립니다. `engine/src/test/.../SignalTest.kt`를 열고 초록 실행 버튼으로 테스트를 돌릴 수 있습니다.

## 4. 자동 테스트 (GitHub Actions)
`.github/workflows/test.yml`이 저장소에 올라가면 push할 때마다 GitHub에서 `gradlew test`가 돕니다. 저장소의 **Actions** 탭에서 결과를 볼 수 있고, 실패하면 빨간 X가 표시됩니다.

## 문제가 생기면
- `JAVA_HOME is not set` → JDK 설치 때 JAVA_HOME 옵션을 켜지 않은 경우. JDK를 다시 설치하거나 환경 변수에 직접 넣습니다.
- `Unsupported class file major version` → JDK가 21이 아닌 경우. `java -version`으로 확인합니다.
- 오류 메시지 전체를 복사해 원래 세션에 붙여 주시면 됩니다.
