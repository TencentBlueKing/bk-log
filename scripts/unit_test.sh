SCRIPT_PATH=$(dirname "$0")
rm -rf /tmp/bk_log
mkdir -p /tmp/bk_log/test_unit/

cp -r $SCRIPT_PATH/../ /tmp/bk_log/test_unit/
cd /tmp/bk_log/test_unit/
source scripts/test_env.sh
pip install -r requirements_dev.txt

virtualenv venv_test --python=python3
source venv_test/bin/activate
sed -i '' '/APIGW_ENABLED/d' dev.env.yml
pip install --upgrade pip==20.3.3
pip install -r requirements.txt

python manage.py test apps.tests --keepdb

rm -rf /tmp/bk_log/test_unit/
