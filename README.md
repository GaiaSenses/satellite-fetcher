# Satellite Fetcher

## Setup
1. Instale o gerenciador de pacotes `conda`. Para uma instalação mais rápida e mínima, use o instalador [Miniconda](https://docs.conda.io/en/latest/miniconda.html).

2. Crie um ambiente isolado para o projeto:
```console
$ conda create --name satfetcher python=3.11 pip
```

3. Ative o ambiente:
```console
$ conda activate satfetcher

(satfetcher) $ # o prompt mudará de acordo com o nome do ambiente
```

4. Instale dependências:
```console
(satfetcher) $ conda install gdal

(satfetcher) $ pip install -r requirements.txt
```

5. Crie arquivo `.env` e defina as variáveis de ambiente:
```console
$ cp .env.example .env
```

6. Execute o servidor
```console
$ python server.py
```
