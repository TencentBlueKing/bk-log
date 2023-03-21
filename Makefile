unittest:
	sh ./scripts/unit_test.sh

build-web:
	cd web && npm install --legacy-peer-deps && npm run build

sync_stag:
	sh ./scripts/git.sh sync_stag

sync_upstream:
	sh ./scripts/git.sh sync_upstream

translate:
	django-admin makemessages --extension py --ignore env_github && django-admin compilemessages

del_py_crypto:
	pip uninstall -y pycrypto
	pip uninstall -y pycryptodome
	pip install pycryptodome