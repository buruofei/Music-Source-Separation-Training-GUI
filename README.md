# MSST-GUI

![MSST-GUI Logo](/images/logo.png)

## Introduction

MSST-GUI is a Qt5-based inference GUI designed to provide a convenient and intuitive way to run inferences (though primarily for personal use). At its core, it's a GUI that uses a specified Python environment to add parameters and call `inference.py`. As such, you can also package `msst_gui_en.py` as a smaller executable file and use it in the main repository.

Please note that I've slightly modified the logic for saving instruments in `inference.py` for ease of use, but it remains compatible with the main repository. The only caveat is that during concatenated inference, it may additionally infer unwanted secondary audio tracks. This is a temporary situation.

![Main Interface](/images/demo1.png)

Inferences are executed sequentially on the target audio from top to bottom. For example, enabling voice separation, harmony separation, and dereverberation simultaneously for a song will directly yield the dry main vocal. Hover your mouse over the corresponding areas to see explanatory information.

![Configuration Editor](/images/demo2.png)

MSST-GUI also comes equipped with a configuration file editor, allowing you to add and use your own models or edit existing ones. Models should be placed in the `pretrain` directory.

## Usage

For English users:
```
python msst_gui_en.py
```

For Chinese users:
```
python msst_gui_zh.py
```

## Features

- User-friendly interface for running audio inferences
- Sequential processing of multiple audio transformations
- Built-in configuration editor for custom model management
- Supports both English and Chinese interfaces
- Compatible with the main repository's `inference.py`

## Requirements

- Python (version X.X or higher)
- Qt5
- Other dependencies (list them here)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/MSST-GUI.git
   ```
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgements

- List any acknowledgements or credits here

For more information or support, please open an issue in this repository.
