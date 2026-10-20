.PHONY: test fumaca grafo install firefly-chrome

PYTHON ?= python

test:
	$(PYTHON) -m pytest testes/ -v

fumaca:
	$(PYTHON) -m pytest testes/test_fumaca.py -v -s

grafo:
	$(PYTHON) -m grafo.gerar_diagrama

firefly-chrome:
	$(PYTHON) abrir_chrome_firefly.py
