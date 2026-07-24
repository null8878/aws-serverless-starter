.PHONY: test deploy clean

test:
	python -m pytest tests/ -v --tb=short

test-cov:
	python -m pytest tests/ -v --tb=short --cov=functions --cov-report=term-missing

deploy:
	sam build
	sam deploy --guided

deploy-prod:
	sam build
	sam deploy --guided --parameter-overrides Stage=prod

clean:
	rm -rf .aws-sam __pycache__ .pytest_cache
	find . -name "*.pyc" -delete
