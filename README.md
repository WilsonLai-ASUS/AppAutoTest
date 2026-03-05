# AppAutoTest
App Auto Test

使用 Black Format

命名規則：
類型            命名方式        範例
class	        PascalCase	    LoginPage
function	    snake_case	    get_user()
variable	    snake_case	    user_name
constant	    ALL_CAPS	    MAX_RETRY
module / file	snake_case	    login_page.py


appium driver install uiautomator2



python3 -m venv venv
source venv/bin/activate

python -m tests.test_launch -app config/app/android_config2.json -dut config/dut/CT8.json
python -m tests.test_first_login -app config/app/android_config2.json -dut config/dut/CT8.json
python -m tests.test_qis_asus_router -app config/app/ios_config.json -dut config/dut/GS-BE18000.json
