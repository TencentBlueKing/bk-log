unittest:
	sh ./scripts/unit_test.sh

build-web:
	cd web && npm install && npm run build

sync:
	sh ./scripts/git.sh sync

translate:
	django-admin makemessages --extension py --ignore env_github && django-admin compilemessages