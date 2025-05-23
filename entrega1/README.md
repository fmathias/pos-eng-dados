# Projeto: Análise Climática e de Consumo por Cidade

Este projeto integra dados de localização, clima e comportamento de consumo para explorar correlações entre ambiente e padrões de uso de serviços, como aluguel de filmes.

## 📦 Estrutura

```
entrega1/
├── data/                  # Dados em diferentes estágios (raw, refined, trusted)
├── utils/                 # Funções auxiliares (conexão, ingestão, visualização, etc)
├── .env                   # Variáveis de ambiente (NÃO versionado)
├── ingestao_bases.py      # Script de ingestão inicial das bases
├── exercicios_aula4.py    # Análises e exercícios aplicados
└── requirements.txt       # Dependências do projeto
```

## 🚀 Funcionalidades

- Ingestão de dados de cidades (Pagila e Geonames)
- Enriquecimento com clima atual via API (WeatherAPI)
- Cálculo de média ponderada de temperatura
- Classificação de qualidade do ar (AQI)
- Visualizações com `matplotlib` e `seaborn`
- Uso de Azure Key Vault para acesso seguro a credenciais

## 🔐 Segurança

Este projeto segue boas práticas de segurança:
- As chaves de API e credenciais estão centralizadas no `.env` (não versionado)
- Integração com **Azure Key Vault** para segredos reais
- O `.gitignore` está configurado para proteger dados sensíveis

> ❗ Caso precise rodar o projeto, crie seu próprio `.env` a partir de um `.env.example` (se aplicável) com as chaves necessárias.

## 🧪 Requisitos

- Python 3.9+
- Azure Identity & Key Vault SDK
- `pandas`, `requests`, `matplotlib`, `seaborn`, etc.

Instale com:

```bash
pip install -r requirements.txt
```

## 👩‍💻 Execução

Exemplo de execução de ingestão:

```bash
python ingestao_bases.py
```

## 📬 Contato

Para dúvidas, sugestões ou contribuições, entre em contato com [Fernanda Mathias](https://github.com/fmathias).
