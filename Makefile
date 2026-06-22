.PHONY: setup load test clean

setup:
	pip install -r requirements.txt

load:
	python src/etl/loader.py

test:
	pytest tests/etl/ -v

clean:
	rmdir /s /q output
	mkdir output