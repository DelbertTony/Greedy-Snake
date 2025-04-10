# Python 贪吃蛇游戏

一个使用 Pygame 开发的现代化贪吃蛇游戏，包含多项特色功能。

## 功能特点

- 经典的贪吃蛇玩法
- 随机生成的障碍物
- 可自定义游戏速度（4-15级）
- 排行榜系统（记录前10名）
- 玩家名称记录
- 游戏暂停功能
- 美观的游戏界面
  - 网格背景
  - 圆角图形
  - 动态蛇头效果

## 下载和安装

### Windows 用户
1. 从 [Releases](https://github.com/yourusername/snake-game/releases) 页面下载最新的 exe 文件
2. 直接运行下载的 exe 文件即可开始游戏

### 开发者安装
1. 克隆仓库：
```bash
git clone https://github.com/yourusername/snake-game.git
cd snake-game
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 运行游戏：
```bash
python snake_game.py
```

## 游戏控制

### 主菜单
- 1: 开始游戏
- 2: 设置
- 3: 排行榜
- 4: 退出

### 游戏中
- 方向键：控制蛇的移动
- 空格键：暂停/继续游戏
- ESC：返回主菜单

### 设置
- 左右方向键：调整游戏速度（4-15）
- ESC：保存并返回

## 游戏操作

- **方向键**：控制蛇的移动
- **空格键**：暂停/继续游戏
- **ESC键**：返回主菜单
- **数字键1-4**：在主菜单中选择选项
- **T键**：在设置中切换主题
- **左右方向键**：在设置中调整游戏速度

## 游戏特点

### 排行榜系统
- 按速度等级分组显示排行榜
- 每个速度等级保存前10名玩家的记录
- 记录包含玩家名称、分数和游戏速度

### 主题系统
- 支持亮色和暗色两种主题
- 所有界面元素都会随主题切换而改变
- 主题设置会被保存

### 速度系统
- 可选择4-15级的游戏速度
- 每个速度等级都有独立的排行榜
- 游戏过程中会随分数提升而加速

## 开发

### 项目结构
```
snake-game/
│
├── snake_game.py      # 主游戏文件
├── build.py           # exe 构建脚本
├── README.md          # 项目说明文档
├── requirements.txt   # 项目依赖
├── .gitignore        # Git忽略文件
├── high_score.json   # 最高分数据文件
└── leaderboard.json  # 排行榜数据文件
```

### 构建 exe
1. 安装构建工具：
```bash
pip install cx_Freeze
```

2. 运行构建脚本：
```bash
python build.py build
```

## 版本历史

### v1.0.0 (2024-xx-xx)
- 初始发布
- 基础游戏功能
- 排行榜系统
- 可自定义速度
- 暂停功能

## 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进游戏。

## 许可证

[添加你的许可证信息]
