# variables
VENV := .venv
PIP := pip
ACTIVATE := $(VENV)\Scripts\activate

install:
	@echo Install dependencies from requirements file...
	@ uv $(PIP) install -r requirements.txt --link-mode=copy


activate:
	@echo Activate venv
	@echo $(ACTIVATE)
