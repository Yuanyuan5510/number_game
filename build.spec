# build.spec
import sys
import os
from PyInstaller.building.api import COLLECT, EXE, PYZ
from PyInstaller.building.build_main import Analysis
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath('.'))

# 基础配置
block_cipher = None
script = 'main.py'
name = 'SWnumbergame'
version_file = 'final_version_info.py'
manifest = 'final_admin_manifest.xml'

# 分析程序依赖
a = Analysis(
    [script],
    pathex=[current_dir],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('server', 'server'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        'PyQt5.QtWebEngineWidgets',
        'flask',
        'flask_socketio',
        'requests',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 打包为单文件
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 配置可执行文件
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',
    version=version_file,
    manifest=manifest,
)