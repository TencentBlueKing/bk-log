unittest:
	sh ./scripts/unit_test.sh

build-web:
	cd web && npm install && npm run build

sync:
	sh ./scripts/git.sh sync

translate:
	django-admin makemessages --extension py --ignore env_github && django-admin compilemessages

del_py_crypto:
	pip uninstall -y pycrypto
	pip uninstall -y pycryptodome
	pip install pycryptodome