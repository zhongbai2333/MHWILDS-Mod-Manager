import sys
from main import main

if __name__ == "__main__":
    sys.argv.append("--core")  # 添加 --core 参数
    main()
