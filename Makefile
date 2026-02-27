#     ____                                   
#    / __ \____  ___  __  ______ ___  ____ _/ /_(_)____
#   / /_/ / __ \/ _ \/ / / / __ `__ \/ __ `/ __/ / ___/
#  / ____/ / / /  __/ /_/ / / / / / / /_/ / /_/ / /__  
# /_/   /_/ /_/\___/\__,_/_/ /_/ /_/\__,_/\__/_/\___/  
#

lock:
	uv lock
sync:
	uv sync
ruff:
	uv run ruff check --fix pneumatic
format:
	uv run ruff format pneumatic
ty:
	uv run ty check pneumatic
test:
	uv run coverage run manage.py test \
		&& uv run coverage report -m

# Runs type-checking, formatting, linting, and unit tests
check: ruff format ty test
