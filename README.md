# Ancient Egyptian ↔ Simplified Chinese Translator
The first open-source bidirectional Ancient Egyptian Hieroglyphs ↔ Simplified Chinese dictionary and translator.
首个开源的古埃及象形文字与简体中文双向词典和翻译工具。


古埃及文字 // 简体中文词典与象形文字翻译工具，支持：

* Unicode 埃及象形文字
* 古埃及语转写
* 中文释义
* 上下文含义
* 本地 GUI

这是一个小型本地工具。

## Project Status / 项目状态

This project is not fully completed yet and is still under active development.

I am currently expanding and improving the dictionary, adding new Ancient Egyptian entries, Chinese meanings, transliterations, contextual meanings, and translation rules.

Contributions, corrections, suggestions, and new dictionary entries are very welcome.

该项目目前尚未完全完成，仍在持续开发中。

我正在继续扩充和改进词典，包括古埃及语词条、中文释义、转写、上下文含义和翻译规则。

非常欢迎提交贡献、修正、建议以及新的词典条目。

## Windows 安装

最简单的方式是运行安装脚本：

```text
install.bat
```

双击 `install.bat` 后，安装程序会自动：

* 安装所需的 Python 依赖
* 将程序编译为独立的 `.exe` 文件
* 将应用安装到本地程序目录
* 在桌面创建应用快捷方式

安装完成后，可以直接通过桌面上的快捷方式启动程序，不需要每次打开终端。

> 首次安装需要联网，以便安装 Pillow 和 PyInstaller。

## 从源代码启动

也可以不安装 `.exe`，直接从终端运行 Python 版本。

确保已安装 Python，然后在项目文件夹中执行：

```bash
python gui.py
```

<img width="967" height="484" alt="Application interface" src="https://github.com/user-attachments/assets/c203abef-f0e1-404e-858d-5b4986b411b4" />

左边输入，右边自动显示翻译结果。

可选翻译方向：

* Auto
* Egyptian → 简体中文
* 简体中文 → Egyptian

## 词典

词典数据保存在：

```text
dictionary.json
```

<img width="678" height="746" alt="Dictionary example" src="https://github.com/user-attachments/assets/4d5273d4-338f-46d9-a643-2b7859cc5439" />

中文转古埃及文字时，`dictionary.json` 中需要存在对应的词条。

没有找到对应词条的汉字会显示为：

```text
[未知:字]
```
