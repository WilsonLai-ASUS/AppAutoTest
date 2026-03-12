#!/bin/zsh

cd "$(dirname "$0")"
set -e

echo "🚀 Appium Automation Environment Setup"
echo ""

########################################
echo "1️⃣ 檢查 Homebrew"
########################################

if ! command -v brew &>/dev/null; then
    echo "安裝 Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    if [[ $(uname -m) == "arm64" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi
else
    echo "Homebrew 已存在"
fi

brew update

########################################
echo "2️⃣ 修正 Xcode path"
########################################

if ! xcode-select -p &>/dev/null; then
    sudo xcode-select -s /Applications/Xcode.app/Contents/Developer
fi

echo "Xcode: $(xcode-select -p)"

########################################
echo "3️⃣ Python 環境設定"
########################################

# 安裝 Python 3.11
if ! brew list python@3.11 &>/dev/null; then
    echo "安裝 Python 3.11..."
    brew install python@3.11
else
    echo "Python 3.11 已安裝"
fi

# 強制 link python（覆蓋舊版）
brew link --force --overwrite python@3.11

# 判斷 brew prefix
BREW_PREFIX=$(brew --prefix)
PYTHON_BIN="$BREW_PREFIX/opt/python@3.11/bin"

# 加入 PATH（當前 session）
export PATH="$PYTHON_BIN:$PATH"

# 永久寫入 .zprofile（login shell）和 .zshrc（interactive shell）
for PROFILE in "$HOME/.zprofile" "$HOME/.zshrc"; do
    if ! grep -q "python@3.11" "$PROFILE" 2>/dev/null; then
        echo "" >> "$PROFILE"
        echo "# Python 3.11 (Homebrew)" >> "$PROFILE"
        echo "export PATH=\"$PYTHON_BIN:\$PATH\"" >> "$PROFILE"
    fi
done

# 建立 alias
for PROFILE in "$HOME/.zprofile" "$HOME/.zshrc"; do
    if ! grep -q "alias python3=" "$PROFILE" 2>/dev/null; then
        echo "alias python=python3.11" >> "$PROFILE"
        echo "alias python3=python3.11" >> "$PROFILE"
    fi
done

# 建立系統層級 symlink，讓所有 shell（包含 GitHub Actions runner）都指向 3.11
SYMLINK_DIR="/usr/local/bin"
sudo mkdir -p "$SYMLINK_DIR"

for CMD in python3 python3.11 pip3; do
    TARGET="$PYTHON_BIN/$CMD"
    LINK="$SYMLINK_DIR/$CMD"
    if [[ -f "$TARGET" ]]; then
        sudo ln -sf "$TARGET" "$LINK"
        echo "✅ symlink: $LINK → $TARGET"
    fi
done

# reload
source "$HOME/.zprofile" 2>/dev/null || true
source "$HOME/.zshrc" 2>/dev/null || true

echo ""
echo "Python path:"
which python3

echo ""
echo "Python version:"
python3 --version

echo ""
echo "Pip version:"
pip3 --version

########################################
echo "4️⃣ Python 套件"
########################################

python3.11 -m pip install --upgrade pip

if ! python3.11 -c "import selenium" &>/dev/null; then
    python3.11 -m pip install selenium
fi

if ! python3.11 -c "import appium" &>/dev/null; then
    python3.11 -m pip install Appium-Python-Client
fi

########################################
echo "5️⃣ 重建 .venv (確保使用 Python 3.11)"
########################################

VENV_DIR="$(pwd)/.venv"

# 檢查現有 venv 是否為 3.11，不是的話就刪掉重建
if [[ -d "$VENV_DIR" ]]; then
    VENV_PYTHON_VER=$("$VENV_DIR/bin/python3" --version 2>&1 | awk '{print $2}')
    if [[ "$VENV_PYTHON_VER" == 3.11* ]]; then
        echo ".venv 已是 Python $VENV_PYTHON_VER，跳過重建"
    else
        echo "⚠️  .venv 目前是 Python $VENV_PYTHON_VER，刪除並重建為 3.11..."
        rm -rf "$VENV_DIR"
    fi
fi

if [[ ! -d "$VENV_DIR" ]]; then
    echo "建立 .venv (Python 3.11)..."
    python3.11 -m venv "$VENV_DIR"
    echo "✅ .venv 建立完成"
fi

# 用 venv 內的 pip 安裝套件
echo "安裝套件到 .venv..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install selenium Appium-Python-Client

if [[ -f "requirements.txt" ]]; then
    echo "從 requirements.txt 安裝..."
    "$VENV_DIR/bin/pip" install -r requirements.txt
fi

echo ""
echo ".venv Python 版本:"
"$VENV_DIR/bin/python3" --version

########################################
echo "6️⃣ Node.js"
########################################

if ! command -v node &>/dev/null; then
    brew install node
else
    echo "Node: $(node -v)"
fi

########################################
echo "7️⃣ CocoaPods"
########################################

if ! command -v pod &>/dev/null; then
    brew install cocoapods
else
    echo "CocoaPods: $(pod --version)"
fi

########################################
echo "8️⃣ ffmpeg"
########################################

if ! command -v ffmpeg &>/dev/null; then
    brew install ffmpeg
else
    echo "ffmpeg: $(ffmpeg -version 2>&1 | head -1)"
fi

########################################
echo "9️⃣ Android tools (adb)"
########################################

if ! command -v adb &>/dev/null; then
    brew install android-platform-tools
fi

########################################
echo "🔟 ios-deploy"
########################################

if ! command -v ios-deploy &>/dev/null; then
    brew install ios-deploy
fi

########################################
echo "1️⃣1️⃣ Carthage"
########################################

if ! command -v carthage &>/dev/null; then
    brew install carthage
fi

########################################
echo "1️⃣2️⃣ Appium"
########################################

if ! command -v appium &>/dev/null; then
    npm install -g appium
else
    echo "Appium: $(appium -v)"
fi

########################################
echo "1️⃣3️⃣ Appium Doctor"
########################################

if ! command -v appium-doctor &>/dev/null; then
    npm install -g appium-doctor
fi

########################################
echo "1️⃣4️⃣ Appium Drivers"
########################################

if ! appium driver list --installed | grep -q xcuitest; then
    appium driver install xcuitest
else
    echo "xcuitest 已安裝"
fi

if ! appium driver list --installed | grep -q uiautomator2; then
    appium driver install uiautomator2
else
    echo "uiautomator2 已安裝"
fi

########################################
echo "1️⃣6️⃣ CocoaPods repo"
########################################

pod repo update || true

########################################
echo "1️⃣7️⃣ Appium Doctor"
########################################

appium-doctor || true

########################################

echo ""
echo "🎉 Setup 完成"
echo ""

echo "Appium version:"
appium -v

echo ""
echo "Installed drivers:"
appium driver list --installed

echo ""
echo "Python version (系統):"
python3 --version

echo ""
echo "Python version (.venv):"
.venv/bin/python3 --version

echo ""
echo "按 Enter 關閉..."
read

