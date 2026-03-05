# test_qis_asus_router.py

"""
測試 QIS ASUS Router 的流程
"""

import sys
from tests.test_base import TestBase
from common import Result, app, dut, Utils, logger, ResultCode
import tests.pages.sky_tree_page as sky_tree_page
import tests.pages.qis_choose_series_page as qis_choose_series_page
import tests.pages.qis_system_setup_page as qis_system_setup_page
import tests.pages.qis_create_wifi_network_page as qis_create_wifi_network_page
import tests.pages.qis_create_iot_network_page as qis_create_iot_network_page
import tests.pages.qis_setup_local_login_account_page as qis_setup_local_login_account_page
import tests.pages.qis_manual_setup_page as qis_manual_setup_page
import tests.pages.qis_setup_guide_join_page as qis_setup_guide_join_page
import tests.pages.qis_system_setup_page_finish as qis_system_setup_page_finish
import tests.pages.tab_bar_home_page as tab_bar_home_page
import tests.pages.tab_bar_settings_page as tab_bar_settings_page


class TestQisAsusRouter(TestBase):

    def test(self) -> Result:

        def steps():
            # sky tree page
            sky_tree_page.tap_setup_button(self)

            # connect wifi
            self.connect_wifi(dut.default_wifi_ssid(), dut.default_wifi_password())

            # choose series page
            if app.is_ios():
                qis_choose_series_page.tap_ios_asus_wifi_7_series(self)
            elif app.is_android():
                qis_choose_series_page.tap_android_asus_wifi_routers(self)

            # qis - system setup page
            qis_system_setup_page.tap_advanced_settings_button(self)

            # qis - manual setup page
            qis_manual_setup_page.tap_dhcp_button(self)
            qis_manual_setup_page.tap_next_button(self)

            # qis - create wifi network page
            if app.is_ios():
                qis_create_wifi_network_page.tap_ios_wifi_network_name_clear_text_button(
                    self
                )
            qis_create_wifi_network_page.fill_wifi_network_name_text_field(self)
            qis_create_wifi_network_page.fill_wifi_network_password_text_field(self)
            qis_create_wifi_network_page.tap_next_button(self)

            # qis - create iot network page
            qis_create_iot_network_page.tap_set_up_later_button(self)

            # qis - setup local login account page
            if dut.is_support_default_password():
                qis_setup_local_login_account_page.tap_use_default_local_login_password_button(
                    self
                )
            if app.is_ios():
                qis_setup_local_login_account_page.tap_ios_username_text_field_clear_text_button(
                    self
                )
            qis_setup_local_login_account_page.fill_username_text_field(self)
            qis_setup_local_login_account_page.fill_password_text_field(self)
            qis_setup_local_login_account_page.fill_confirm_password_text_field(self)
            qis_setup_local_login_account_page.tap_next_button(self)

            # qis - setup guide join page
            qis_setup_guide_join_page.wait_connect_to_your_wifi_label(self)
            qis_setup_guide_join_page.reconnect_wifi(self)

            # qis - system setup page finish
            qis_system_setup_page_finish.wait_finish_button(self)
            qis_system_setup_page_finish.tap_finish_button(self)

            """
            #sky_tree_page.tap_login_button(self)
            
            import tests.pages.login_page as login_page
            #login_page.login(self)
            """

            # home page
            tab_bar_home_page.tap_first_enter_home_page_alerts(self)
            tab_bar_home_page.tap_tab_bar_settings_button(self)

            # settings page
            tab_bar_settings_page.tap_tab_bar_settings_button(self)
            tab_bar_settings_page.tap_feature_label(self, "System Settings")
            tab_bar_settings_page.tap_feature_label(self, "Factory Default")
            tab_bar_settings_page.confirm_factory_default(self)

        return self.run_test(steps)


def main(argv=None):
    test = TestQisAsusRouter(argv or sys.argv)
    test.finish(test.test())


if __name__ == "__main__":
    main()
