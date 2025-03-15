import PyInstaller.__main__

PyInstaller.__main__.run([
    'snake_game.py',
    '--onefile',
    '--windowed',
    '--add-data', 'high_score.json;.',
    '--add-data', 'leaderboard.json;.',
    '--name', 'SnakeGame'
])