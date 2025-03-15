import PyInstaller.__main__
import os

# 检查图标文件是否存在
if not os.path.exists('snake_icon.ico'):
    print("警告: snake_icon.ico 文件不存在！将使用默认图标。")
    icon_option = []
else:
    icon_option = ['--icon=snake_icon.ico']

# 构建命令
build_options = [
    'snake_game.py',
    '--onefile',
    '--windowed',
    '--add-data', 'high_score.json;.',
    '--add-data', 'leaderboard.json;.',
    '--name', 'SnakeGame',
    '--clean'  # 清理之前的构建文件
]

# 添加图标选项（如果图标文件存在）
build_options.extend(icon_option)

# 开始构建
print("正在构建exe文件...")
PyInstaller.__main__.run(build_options) 