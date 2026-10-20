.PHONY: test fumaca grafo install

PYTHON ?= python

test:
	$(PYTHON) -m pytest testes/ -v

fumaca:
	$(PYTHON) -m pytest testes/test_fumaca.py -v -s

grafo:
	$(PYTHON) -m grafo.gerar_diagrama
