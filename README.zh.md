[# English](README.en.md) | [Español](README.md) | [中文](README.zh.md)

# heuristica

## 简介

本仓库包含用于解决**约束满足问题（CSP）**与**路径搜索**问题的 Python 脚本。脚本按功能与用途划分到不同目录中。

## 仓库结构

仓库结构如下：

- `enunciado/`：包含多个不同问题的 Python 脚本。
  - `alumnos.py`：用于解决与学生相关的约束满足问题（CSP）的脚本。
  - `n-queens.py`：使用约束处理来求解 N 皇后问题的脚本。
  - `n-queens-fun.py`：`n-queens.py` 的改写版本，采用不同的实现思路。
  - `sum-words.py`：使用约束处理来求解 “sum-words” 文字算式谜题的脚本。
- `parte-1/`：项目第一部分的脚本与测试文件。
  - `CSP-calls.sh`：用于运行 CSP 相关测试的 shell 脚本。
  - `CSP-tests/`：CSP 的测试文件目录。
  - `CSPMaintenance.py`：使用约束处理来解决维护排程问题的 Python 脚本。
- `parte-2/`：项目第二部分的脚本与测试文件。
  - `ASTAR-calls.sh`：用于运行路径搜索相关测试的 shell 脚本。
  - `ASTAR-tests/`：A* 的测试文件目录。
  - `ASTARRodaje.py`：使用 A* 算法解决路径搜索问题的 Python 脚本。
- `.gitignore`：指定 Git 应忽略的文件与目录。
- `requirements.txt`：项目依赖列表。

## 安装

按以下步骤配置环境并安装依赖：

1. 克隆仓库：

   ```bash
   git clone https://github.com/liangjizhu/heuristica.git
   cd heuristica
   ```

2. 创建虚拟环境：

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. 安装依赖：

   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

### 运行约束满足（CSP）脚本

运行 CSP 脚本可使用以下命令：

- `alumnos.py`：

  ```bash
  python enunciado/alumnos.py
  ```

- `n-queens.py`：

  ```bash
  python enunciado/n-queens.py
  ```

- `n-queens-fun.py`：

  ```bash
  python enunciado/n-queens-fun.py
  ```

- `sum-words.py`：

  ```bash
  python enunciado/sum-words.py
  ```

### 运行维护排程脚本

运行维护排程脚本：

```bash
python parte-1/CSPMaintenance.py <ruta_fichero_entrada>
```

### 运行路径搜索脚本

运行路径搜索脚本：

```bash
python parte-2/ASTARRodaje.py <path mapa.csv> <num-h>
```

### 运行测试

运行测试：

- CSP 测试：

  ```bash
  bash parte-1/CSP-calls.sh
  ```

- A* 测试：

  ```bash
  bash parte-2/ASTAR-calls.sh
  ```
