# AppAutoTest

用 Python + Appium 跑 iOS/Android E2E 測試。

## Prerequisites

- macOS + Python 3
- Appium Server（預設 `http://127.0.0.1:4723`）
- 真機與對應工具
	- iOS：Xcode / WebDriverAgent
	- Android：adb / UiAutomator2

## Local setup (recommended)

本專案依賴 `selenium`、`Appium-Python-Client` 等套件。建議使用 virtualenv，避免污染系統 Python（也可避免 macOS 常見的 PEP 668 問題）。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run tests

請在 repo root 執行，並使用 `-m`（module mode）。

### iOS

```bash
python -m tests.test_qis_asus_router \
	-app config/app/ios_config.json \
	-dut config/dut/GS-BE18000.json
```

### Android

```bash
python -m tests.test_qis_asus_router \
	-app config/app/android_config.json \
	-dut config/dut/GS-BE18000.json
```

## Config

- App config：`config/app/*.json`
	- `udid`：要連的真機 UDID
	- `app_path`：App 檔案路徑（例如 `apps/ios/AsusRouter.ipa` / `apps/android/AsusRouter.apk`）
- DUT config：`config/dut/*.json`

## Artifacts

測試執行會輸出到 `results/`，並以 timestamp 建資料夾，包含：logs / screenshots / videos / reports。

## CI / self-hosted runner notes

- `*.ipa` / `*.apk` 預設會被 `.gitignore` 忽略，因此 GitHub Actions checkout 後通常不會有 app binary。
	- 若你要 CI 使用「runner 本機檔案」，可在 workflow 內把 runner 的絕對路徑 copy 到 workspace 的 `app_path`。
- 如果看到 `ModuleNotFoundError: selenium`：通常是沒裝依賴，請先跑上面的 venv 安裝步驟。

## Style

- Format：Black

## 命名規則

| 類型 | 命名方式 | 範例 |
| --- | --- | --- |
| class | PascalCase | LoginPage |
| function | snake_case | get_user() |
| variable | snake_case | user_name |
| constant | ALL_CAPS | MAX_RETRY |
| module / file | snake_case | login_page.py |