.PHONY: cluster build deploy test simulate operator-dev

cluster:
	./scripts/cluster-setup.sh

build:
	./scripts/build-images.sh

deploy: build
	./scripts/deploy.sh

test:
	docker build -t bloodstream/circulation:latest ./circulation
	docker run --rm -e BLOODSTREAM_CONFIG=chrome-latest -e TRAFFIC_CLASS=corridor bloodstream/circulation:latest

simulate:
	./scripts/simulate-circulation.sh

operator-dev:
	cd operator && pip install -r requirements.txt && python main.py
