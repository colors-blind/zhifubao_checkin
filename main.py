"""入口脚本：连接设备并启动支付宝。"""

from __future__ import annotations

from app_controller import AppController
from common_actions import CommonActions
from config import ALIPAY_PACKAGE, DEFAULT_DEVICE_SERIAL, LAUNCH_TIMEOUT
from device_manager import DeviceManager


def main() -> None:
    device = DeviceManager(DEFAULT_DEVICE_SERIAL).connect()

    # 初始化常用动作封装，方便后续扩展自动化流程
    _ = CommonActions(device)

    app = AppController(device)
    app.start_app(ALIPAY_PACKAGE, wait=True, timeout=LAUNCH_TIMEOUT)
    print("已启动支付宝。")


if __name__ == "__main__":
    main()
