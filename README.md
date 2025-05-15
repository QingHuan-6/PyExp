## 运行此项目须知

**环境要求:**

* **Python 版本:** 3.9

**数据库配置:**

1.  **创建数据库:**
    * 请在 MySQL 数据库中创建一个名为 `house_price` 的数据库。

2.  **修改数据库连接:**
    * 编辑项目主目录下的 `config.py` 文件。
    * 根据您的 MySQL 数据库配置，修改其中的数据库连接信息（例如：主机名、用户名、密码等）。

3.  **创建数据表:**
    * 导航到 `app` 文件夹：
        ```bash
        cd app
        ```
    * 运行 `init.py` 文件以创建项目所需的数据表：
        ```bash
        python init.py
        ```

**后端运行步骤:**

1.  **安装依赖:**
    * 确保您位于项目主目录下。
    * 使用 pip 安装项目所需的 Python 依赖包：
        ```bash
        pip install -r requirements.txt
        ```

2.  **启动后端服务:**
    * 在项目主目录下运行 `run.py` 文件：
        ```bash
        python run.py
        ```

**前端运行步骤:**

1.  **导航到前端目录:**
    ```bash
    cd front
    ```

2.  **安装前端依赖:**
    ```bash
    npm install
    ```

3.  **启动前端服务:**
    ```bash
    npm run serve
    ```
