.PHONY: cluster build deploy demo test simulate operator-dev

cluster:
	./scripts/cluster-setup.sh

build:
	./scripts/build-images.sh

deploy: build
	./scripts/deploy.sh

demo:
	cd demo-app && docker compose up --build

test:
	cd e2e && npm install && npx playwright install chromium && BLOODSTREAM_CONFIG=chrome-latest npm test

simulate:
	./scripts/simulate-circulation.sh

operator-dev:
	cd operator && pip install -r requirements.txt && python main.py
