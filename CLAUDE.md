# CLAUDE.md - Documentação do Projeto

## Visão Geral do Projeto

Este é um repositório de estudos pessoal que contém múltiplos projetos e disciplinas acadêmicas. O foco principal está na pasta `Personal/` que contém um sistema de monitoramento de preços de e-commerce desenvolvido em Python e Node.js, hospedado no Google Cloud Platform.

## Estrutura Principal

### Personal/ - Sistema de Monitoramento de Preços

**Descrição**: Sistema completo de web scraping para monitoramento de preços em múltiplas lojas online brasileiras, com integração a banco de dados PostgreSQL e Google Cloud Functions.

**Tecnologias Principais**:
- **Backend**: Python (Google Cloud Functions)
- **Banco de Dados**: PostgreSQL (Neon Database)
- **Orquestração**: Google Cloud Tasks
- **Web Scraping**: ScraperAPI + BeautifulSoup
- **Scheduler**: Node.js

#### Arquivos Principais

**Scrapers Python** (Google Cloud Functions):
- `amazon_scraper.py` - Scraper para Amazon Brasil
- `mercadolivre_scraper.py` - Scraper para Mercado Livre
- `magalu_scraper.py` - Scraper para Magazine Luiza
- `americanas_scraper.py` - Scraper para Americanas
- `fastshop_scraper.py` - Scraper para FastShop
- `cea_scraper.py` - Scraper para C&A
- `aliexpress_scraper.py` - Scraper para AliExpress

**Gerenciamento e Orquestração**:
- `scheduler_manager.js` - Gerenciador principal de tarefas (Node.js)
- `database_checker.py` - Verificador de banco de dados
- `zyte.py` - Utilitário para Zyte (ScraperAPI)

**APIs e Utilitários**:
- `replicate_api.py` - Integração com Replicate AI para geração de modelos 3D

#### Arquitetura do Sistema

1. **Banco de Dados**: Tabela `monitors` com campos:
   - `id`, `user_id`, `url`, `store`
   - `price`, `product_name`, `name`
   - `desired_price`, `notification_platform`
   - `is_below_desired_price` (boolean)
   - Timestamps: `last_mined_at`, `next_mine_at`, `created_at`, `updated_at`

2. **Fluxo de Funcionamento**:
   - Scheduler verifica produtos para mineração (`next_mine_at <= CURRENT_TIMESTAMP`)
   - Cria tarefas no Google Cloud Tasks para cada scraper
   - Scrapers extraem preços via ScraperAPI
   - Dados são salvos/atualizados no banco PostgreSQL
   - Próxima mineração agendada para 1 hora

3. **Lojas Suportadas**:
   - Amazon, Mercado Livre, Magazine Luiza
   - Americanas, FastShop, C&A, AliExpress

#### Configurações e Dependências

**Python (requirements.txt)**:
```
functions-framework==3.*
requests==2.31.0
beautifulsoup4==4.12.2
psycopg2-binary==2.9.9
```

**Node.js (package.json)**:
```json
{
  "dependencies": {
    "@google-cloud/functions-framework": "^3.3.0",
    "@google-cloud/tasks": "^5.1.0",
    "pg": "^8.11.3"
  }
}
```

#### Padrões de Código

**Classes de Scraper**:
- Padrão consistente em todos os scrapers
- Método `fetch_product_html_via_scraperapi()` para obter HTML
- Método `extract_price_from_html()` para parsing
- Método `_parse_price_to_decimal()` para conversão de preços brasileiros
- Método `run()` como ponto de entrada

**Tratamento de Preços**:
- Suporte ao formato brasileiro (R$ 1.234,56)
- Conversão automática de separadores de milhares
- Uso de `Decimal` para precisão monetária

**Google Cloud Functions**:
- Decorador `@functions_framework.http`
- Recebimento de JSON com `url`, `userId`, `name`, `desired_price`
- Retorno padronizado com preço, metadados e status

### Outras Pastas do Projeto

**Probest/**: Estudos de modelos probabilísticos
- `Atividade_aula15.ipynb`
- `modelos_probabilísticos.ipynb`

**Searchly/**: Projeto C# (.NET 9.0)
- Sistema de gerenciamento de tarefas
- Entity Framework com SQLite
- Interface de linha de comando

**Sistemas Operacionais/**: Estudos de SO
- `lab1.c` - Laboratório em C

**Software Basico/**: Estudos de Assembly
- Documentação em Markdown
- Códigos em Assembly
- Provas antigas

**Udemy/**: Cursos online
- `Javascript/Inicio/teste.js`

## Configurações de Ambiente

### Banco de Dados
- **Provedor**: Neon PostgreSQL
- **Connection String**: `postgresql://neondb_owner:npg_MQphA3BFf0gP@ep-wispy-bonus-acat1phz-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require`

### Google Cloud Platform
- **Project ID**: `deploy-461918`
- **Location**: `southamerica-east1`
- **Queues**: `tagfy-queue`, `tagfy-queue-tasks`

### APIs Externas
- **ScraperAPI**: `9f5a0cdc28ed693568ca66e8a7baac2d`
- **Replicate**: Configurado via variável de ambiente

## Padrões de Desenvolvimento

### Comentários e Documentação
- Seguir estilo Google para docstrings
- Comentários em português
- Explicar o "porquê" ao invés do "como"
- Evitar comentários óbvios ou genéricos

### Estrutura de Código
- Classes bem definidas com responsabilidades claras
- Tratamento de erros consistente
- Uso de tipos Python modernos (Decimal, Union, Optional)
- Padrões de nomenclatura consistentes

### Deploy e Infraestrutura
- Google Cloud Functions para cada scraper
- Cloud Tasks para orquestração
- Neon PostgreSQL para persistência
- Timezone configurado para America/Sao_Paulo

## Contexto de Uso

Este projeto é usado para:
1. Monitoramento automático de preços de produtos
2. Notificações quando preços ficam abaixo do desejado
3. Estudos acadêmicos em múltiplas disciplinas
4. Experimentação com APIs de IA (Replicate)

## Observações Importantes

- O sistema está em produção no Google Cloud
- Credenciais estão hardcoded (considerar variáveis de ambiente)
- Suporte a múltiplas lojas brasileiras
- Sistema de agendamento automático de tarefas
- Integração com notificações (plataforma configurável)
