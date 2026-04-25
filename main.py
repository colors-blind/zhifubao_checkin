"""入口脚本：通用应用自动化测试流程示例。"""

from __future__ import annotations

from app_automation import AppAutomation, create_alipay_config, create_wechat_config, AppConfig
from config import DEFAULT_DEVICE_SERIAL


def run_alipay_flow() -> None:
    """运行支付宝自动化流程示例。"""
    print("=" * 50)
    print("支付宝自动化测试流程")
    print("=" * 50)
    
    automation = AppAutomation(DEFAULT_DEVICE_SERIAL)
    alipay_config = create_alipay_config()
    
    success = automation.run_app_flow(alipay_config)
    
    if success:
        print("\n✓ 支付宝自动化流程执行成功！")
    else:
        print("\n✗ 支付宝自动化流程执行失败！")


def list_installed_payment_apps() -> None:
    """列出设备上所有支付相关的应用。"""
    print("\n" + "=" * 50)
    print("设备上的支付相关应用")
    print("=" * 50)
    
    automation = AppAutomation(DEFAULT_DEVICE_SERIAL)
    payment_apps = automation.find_all_app_packages("pay")
    
    if payment_apps:
        for i, app in enumerate(payment_apps, 1):
            print(f"{i}. {app}")
    else:
        print("未找到支付相关应用")


def main() -> None:
    """主函数：运行支付宝自动化流程。"""
    list_installed_payment_apps()
    run_alipay_flow()


if __name__ == "__main__":
    main()
