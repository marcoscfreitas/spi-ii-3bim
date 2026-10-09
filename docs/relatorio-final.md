# Relatório final do projeto

## 1. Identificação

- Disciplina: Sistemas para Internet II
- Integrantes: Pedro, Marcos e Alex
- Período planejado de execução: 12/09/2026 a 12/10/2026
- Prazo de entrega: 13/10/2026

## 2. Objetivo

Apresentar o desenvolvimento da aplicação full stack para consulta de informações públicas de servidores ativos e aposentados do Poder Executivo Federal, incluindo organização da equipe, decisões técnicas, validações e resultados.

## 3. Equipe e divisão de responsabilidades

| Integrante | Responsabilidades principais |
|---|---|
| Pedro | Liderança técnica, infraestrutura, QA e documentação de gestão |
| Marcos | Banco de dados e backend |
| Alex | Frontend |

Até o corte, a divisão efetivamente entregue foi:

| Integrante | Sprint 1 | Sprint 2 concluída até 09/10/2026 |
|---|---|---|
| Pedro | `INF-01` a `INF-08`, `QA-01`, `QA-02`, `LID-01` e `LID-02` | `INF-09` a `INF-12`, `QA-03` a `QA-06` e `LID-03` a `LID-07` |
| Marcos | `BD-01` a `BD-08` e `BACK-01` a `BACK-06` | `BACK-07` a `BACK-15` e `BD-09` |
| Alex | `FRONT-01` a `FRONT-10` | `FRONT-11` a `FRONT-20` |

As atividades normais das duas sprints foram concluídas. A atividade opcional
`BONUS-01` não integra a carga planejada das sprints e não foi iniciada.

## 4. Metodologia e organização das sprints

O desenvolvimento foi dividido em duas sprints de 15 dias: a Sprint 1, de
12/09 a 26/09/2026, e a Sprint 2, de 27/09 a 11/10/2026, com 12/10 reservado
para o fechamento antes da entrega. O Jira foi utilizado para registrar as
atividades, os responsáveis, os Story Points e o andamento de cada item.

As tasks receberam estimativas de 1 ou 2 Story Points. A ordem de execução
acompanhou as dependências do projeto: estrutura e banco de dados na primeira
etapa; implementação e integração de backend e frontend na sequência; testes,
correções e documentação no fechamento. A Sprint 1 totalizou 56 pontos. Com a
inclusão de `LID-07/PROJ-72` em 09/10, a Sprint 2 passou de 57 para 59 pontos.

As mudanças foram desenvolvidas em branches identificadas pela área e pela
chave do Jira. Cada commit correspondeu a uma task e preservou a autoria do
responsável. Tasks relacionadas do mesmo integrante e da mesma área puderam
compartilhar uma branch e uma Pull Request, sem misturar suas alterações no
mesmo commit. As integrações foram realizadas em `dev`.

O acompanhamento considerou o quadro do Jira, o histórico Git e as evidências
produzidas por cada atividade. Dias sem entrega integrada foram mantidos
explicitamente no registro e no burndown, sem atribuir trabalho ou resultados
que não possuíssem evidência.

## 5. Arquitetura e execução

A aplicação possui três serviços orquestrados pelo Docker Compose:

- `db`: PostgreSQL 18 Alpine, responsável pelo schema, pelos índices e pela
  extensão `pg_trgm`;
- `backend`: Python 3.14, Flask 3.1.3, Gunicorn 26.2.0 e psycopg 3.3.5;
- `frontend`: React 19 com TypeScript, Vite 8 e Tailwind CSS 4, executado pelo
  servidor de preview do Vite.

O navegador acessa o frontend pela porta `5173`. As requisições iniciadas em
`/api` são encaminhadas pelo proxy do Vite ao backend na porta interna `8000`.
O backend acessa o PostgreSQL pelo nome de serviço `db`. O banco não publica
sua porta para o host.

O backend é iniciado com um processo Gunicorn e quatro threads. O Compose
limita a API a duas buscas simultâneas e configura timeout de 2.000 ms para as
consultas. Os serviços de banco e backend possuem healthchecks, e os três usam
a política `restart: unless-stopped`.

A raiz contém `backend/`, `frontend/`, `db/`, `docs/`, `tests/` e
`docker-compose.yml`. A aplicação pode ser construída e iniciada com:

```powershell
docker compose up --build
```

O arquivo `.env` é opcional para a execução local. O Compose fornece valores
padrão, enquanto `.env.example` registra as variáveis substituíveis de conexão
com o banco, limite de concorrência e timeout das consultas.

## 6. Tratamento e organização dos dados

Foram analisados os conjuntos públicos Gestão de Pessoas do Executivo Federal -
Aposentados e Gestão de Pessoas do Executivo Federal - Carreiras/Cargos. A
inspeção abrangeu as competências de setembro de 2025 a agosto de 2026. Os
recursos de agosto de 2026 estavam indisponíveis, e o arquivo de Aposentados de
dezembro de 2025 estava vazio.

Os campos utilizados foram limitados a nome, cargo, órgão e UF. CPF, matrícula,
remuneração e os demais dados pessoais ou funcionais não foram incorporados. A
UF não existe no conjunto de Aposentados e, por isso, permanece nula nesses
registros.

Os arquivos usam codificação Latin-1 e separação por ponto e vírgula. O
tratamento remove bytes NUL e espaços excedentes; ignora linhas vazias,
cabeçalhos e linhas de identificação; trata o delimitador final adicional de
Carreiras/Cargos; valida a quantidade de colunas e os campos obrigatórios;
normaliza a UF; rejeita UFs malformadas; remove registros idênticos dentro de
cada arquivo; e gera um CSV UTF-8 com origem, arquivo e linha do registro.

O modelo relacional contém as tabelas `servidor`, `cargo`, `orgao` e `uf`. A
importação usa uma tabela temporária, insere os valores distintos nas tabelas
de domínio e cria os relacionamentos em `servidor`. O processo exige tabelas de
destino vazias e compara a quantidade inserida com a quantidade da tabela
temporária. Uma divergência interrompe a importação. Não existe no repositório
um registro persistido da contagem final de uma importação pública; por isso,
nenhum total importado é atribuído neste relatório.

A extensão `pg_trgm` sustenta a busca por similaridade. O nome do servidor usa
índice GiST, compatível com a ordenação por distância textual. Cargo e órgão
possuem índices trigram GIN, e as chaves estrangeiras de cargo, órgão e UF
possuem índices B-tree.

## 7. Funcionalidades implementadas

### 7.1 Backend

A API disponibiliza `GET /health` e `GET /api/servidores`. A consulta aceita
filtros exatos por nome, cargo, UF e órgão, busca aproximada por nome e
combinações entre os filtros. A similaridade aceita `limit` entre 1 e 100, com
valor padrão 100. A paginação usa `page` e `page_size`, limitada a 100 registros
por página, e informa página atual, tamanho, total de registros e total de
páginas.

Todas as respostas seguem um envelope JSON com `sucesso`, `mensagem` e `dados`;
respostas paginadas também incluem `paginacao`. A API diferencia registro único,
múltiplos registros, ausência de resultados e página inexistente.

Os parâmetros são validados antes do acesso ao banco. A UF precisa pertencer à
lista de siglas brasileiras, valores numéricos precisam estar nos limites
definidos e parâmetros desconhecidos são rejeitados. As consultas usam
parâmetros separados do SQL, e entradas compatíveis com tentativas de injeção
são recusadas. A API retorna falhas controladas para entrada inválida, recurso
inexistente, método não permitido, excesso de concorrência, falha interna e
timeout. O limite de duas buscas simultâneas retorna HTTP 429 ao excedente, e o
cancelamento de consulta pelo PostgreSQL é convertido em HTTP 504.

### 7.2 Frontend

O frontend apresenta um formulário com nome, modo de busca exata ou por
similaridade, limite da similaridade, cargo, UF e órgão. Os filtros podem ser
utilizados isoladamente ou em conjunto. A interface não envia uma busca ao
abrir a página e impede o envio sem nenhum filtro.

Cada consulta usa páginas de dez registros. A navegação oferece ações anterior
e próxima e até cinco números de página visíveis. A interface diferencia
resultado único, lista de resultados, carregamento, ausência de resultados e
erro.

As respostas da API são verificadas antes da renderização. Falhas de rede, JSON
inválido e estruturas incompatíveis produzem mensagens controladas. Uma busca
válida sem registros apresenta o estado vazio; uma página inexistente continua
sendo apresentada como erro. O layout é responsivo e utiliza elementos
semânticos, rótulos, indicação de página atual, regiões de status e alertas. A
identidade visual segue como referência o Portal Brasileiro de Dados Abertos.

### 7.3 Comportamento sob carga

Em 04/10/2026, a API e o PostgreSQL foram executados pela composição Docker do projeto. O banco de teste recebeu 100.000 servidores sintéticos, gerados com `generate_series(1, 100000)`, todos associados a um cargo, um órgão e à UF RS. A carga usou a busca `GET /api/servidores?similar=Servidor&limit=100`, que percorre o caminho completo entre API e banco. O backend estava configurado com um processo Gunicorn, quatro threads, limite de duas buscas simultâneas e timeout SQL de 2.000 ms.

No cenário de capacidade, foram realizadas 20 requisições com concorrência 2. Todas retornaram HTTP 200, sem erro de transporte. A execução durou 2,921 s, com vazão de 6,85 requisições por segundo, latência mediana de 276,08 ms, p95 de 367,76 ms e máxima de 378,41 ms. Após a carga, o endpoint de saúde respondeu HTTP 200 em 23,34 ms.

No cenário de sobrecarga, foram realizadas 200 requisições com concorrência 32. Duas buscas retornaram HTTP 200 e 198 foram rejeitadas com HTTP 429 e a mensagem JSON `limite de buscas simultaneas excedido`. Não houve erro de transporte nem status inesperado. As rejeições tiveram latência mediana de 34,12 ms e p95 de 43,66 ms; as duas buscas aceitas concluíram entre 363,25 ms e 364,60 ms. Após a carga, o endpoint de saúde respondeu HTTP 200 em 2,78 ms. O serviço permaneceu disponível e o excedente falhou de forma controlada, atendendo ao critério do teste.

Os cenários podem ser repetidos sem dependências adicionais:

```powershell
python tests/load_test.py "http://localhost:8000/api/servidores?similar=Servidor&limit=100" --requests 20 --concurrency 2 --timeout 10
python tests/load_test.py "http://localhost:8000/api/servidores?similar=Servidor&limit=100" --requests 200 --concurrency 32 --timeout 10
```

Os resultados completos estão em [teste-carga-capacidade-2026-10-04.json](./evidencias/teste-carga-capacidade-2026-10-04.json) e [teste-carga-2026-10-04.json](./evidencias/teste-carga-2026-10-04.json).

## 8. Divisão das tasks e histórico de commits

### 8.1 Critério de apuração

O histórico abaixo foi conferido na linha integrada de `dev` até o merge
`43667cc`, considerando os commits sem merge até `e5647e8`. Foram usados a
data, o autor e a mensagem registrados em cada commit. A atividade
`INF-02/PROJ-4`, concluída no Jira sem alteração de código, foi mantida no
registro diário com essa ressalva. `LID-03/PROJ-47` corresponde à consolidação
desta seção. `LID-07/PROJ-72` corresponde ao próprio commit que finaliza este
relatório e, por isso, é registrada por autorreferência.

A data do commit indica quando a evidência entrou no histórico Git. Ela não é
usada para afirmar horas trabalhadas nem atividades que não produziram commit.
O acompanhamento detalhado da primeira sprint está em
[acompanhamento-sprint-1.md](./acompanhamento-sprint-1.md).

### 8.2 Registro diário

#### Sprint 1

| Data | Pedro | Marcos | Alex |
|---|---|---|---|
| 12/09 | `INF-01/PROJ-3` | — | — |
| 13/09 | `INF-02/PROJ-4` (gestão, sem commit) | `BD-01/PROJ-15`, `BD-02/PROJ-16` | `FRONT-01/PROJ-29`, `FRONT-02/PROJ-30` |
| 14/09 | `INF-03/PROJ-5` | `BD-03/PROJ-17` | `FRONT-03/PROJ-31` |
| 15/09 | `INF-04/PROJ-6` | `BD-04/PROJ-18` | `FRONT-04/PROJ-32` |
| 16/09 | `INF-05/PROJ-7` | `BD-05/PROJ-19` | `FRONT-05/PROJ-33` |
| 17/09 | Sem entrega integrada | Sem entrega integrada | Sem entrega integrada |
| 18/09 | `INF-06/PROJ-8`, `INF-07/PROJ-9` | `BD-06/PROJ-20` | `FRONT-06/PROJ-34`, `FRONT-07/PROJ-35` |
| 19/09 | Sem entrega integrada | Sem entrega integrada | Sem entrega integrada |
| 20/09 | `INF-08/PROJ-10`, `QA-01/PROJ-11` | `BD-07/PROJ-21`, `BD-08/PROJ-22`, `BACK-01/PROJ-23` | `FRONT-08/PROJ-36`, `FRONT-09/PROJ-37` |
| 21/09 | Sem entrega integrada | Sem entrega integrada | Sem entrega integrada |
| 22/09 | Sem entrega integrada | Sem entrega integrada | Sem entrega integrada |
| 23/09 | `QA-02/PROJ-12`, `LID-02/PROJ-14`; atualização de `LID-01/PROJ-13` | `BACK-02/PROJ-24`, `BACK-03/PROJ-25`, `BACK-04/PROJ-26` | `FRONT-10/PROJ-38` |
| 24/09 | Sem entrega integrada | Sem entrega integrada | Sem entrega integrada |
| 25/09 | Sem entrega integrada | Sem entrega integrada | Sem entrega integrada |
| 26/09 | conclusão de `LID-01/PROJ-13` | `BACK-05/PROJ-27`, `BACK-06/PROJ-28` | Sem entrega integrada |

#### Sprint 2 até 09/10/2026

| Data | Pedro | Marcos | Alex |
|---|---|---|---|
| 27/09 | `INF-09/PROJ-39` | `BACK-07/PROJ-51` | `FRONT-11/PROJ-61`, `FRONT-12/PROJ-62` |
| 28/09 | Sem entrega integrada | Sem entrega integrada | Sem entrega integrada |
| 29/09 | Sem entrega integrada | Sem entrega integrada | Sem entrega integrada |
| 30/09 | `INF-10/PROJ-40`, `INF-11/PROJ-41`, `INF-12/PROJ-42` | `BACK-08/PROJ-52`, `BACK-09/PROJ-53`, `BACK-10/PROJ-54` | `FRONT-13/PROJ-63`, `FRONT-14/PROJ-64`, `FRONT-15/PROJ-65` |
| 01/10 | Sem entrega integrada | Sem entrega integrada | Sem entrega integrada |
| 02/10 | Sem entrega integrada | Sem entrega integrada | Sem entrega integrada |
| 03/10 | Sem entrega integrada | Sem entrega integrada | Sem entrega integrada |
| 04/10 | `QA-03/PROJ-43`, `QA-04/PROJ-44`, `QA-05/PROJ-45`, `QA-06/PROJ-46` | `BACK-11/PROJ-55`, `BACK-12/PROJ-56`, `BD-09/PROJ-57`, `BACK-13/PROJ-58` | `FRONT-16/PROJ-66`, `FRONT-17/PROJ-67`, `FRONT-18/PROJ-68`, `FRONT-19/PROJ-69` |
| 05/10 | Sem entrega integrada | Sem entrega integrada | Sem entrega integrada |
| 06/10 | `LID-03/PROJ-47`, `LID-04/PROJ-48` | `BACK-14/PROJ-59`, `BACK-15/PROJ-60` | `FRONT-20/PROJ-70` |
| 07/10 | Sem entrega integrada | Sem pendências normais | Sem pendências normais |
| 08/10 | Sem entrega integrada | Sem pendências normais | Sem pendências normais |
| 09/10 | `LID-05/PROJ-49`, `LID-06/PROJ-50`, `LID-07/PROJ-72` | Sem pendências normais | Sem pendências normais |

### 8.3 Histórico de commits por integrante

#### Pedro

| Data | Task/Jira | Commit(s) | Resultado registrado |
|---|---|---|---|
| 12/09 | `INF-01/PROJ-3` | `82574ee`, `0a50fb5` | estrutura inicial ajustada para a raiz |
| 14/09 | `INF-03/PROJ-5` | `c8395e6` | composição inicial criada |
| 15/09 | `INF-04/PROJ-6` | `9785ee7` | imagem do banco criada |
| 16/09 | `INF-05/PROJ-7` | `e4be7c3` | imagem do backend criada |
| 18/09 | `INF-06/PROJ-8` | `580e9ef` | imagem do frontend criada |
| 18/09 | `INF-07/PROJ-9` | `3baff68` | orquestração dos containers validada |
| 20/09 | `INF-08/PROJ-10` | `493c300` | variáveis de ambiente configuradas |
| 20/09 | `QA-01/PROJ-11` | `edf7e9d` | plano de testes da API definido |
| 23/09 | `QA-02/PROJ-12` | `b12a706` | casos de SQL injection definidos |
| 23 e 26/09 | `LID-01/PROJ-13` | `79ef587`, `5236647` | acompanhamento da Sprint 1 registrado e encerrado |
| 23/09 | `LID-02/PROJ-14` | `26cd934` | estrutura do relatório final criada |
| 27/09 | `INF-09/PROJ-39` | `467b7a3` | aplicação integrada à composição |
| 30/09 | `INF-10/PROJ-40` | `fcc9fb3` | healthchecks e reinício configurados |
| 30/09 | `INF-11/PROJ-41` | `555a6a3` | buscas simultâneas limitadas |
| 30/09 | `INF-12/PROJ-42` | `dd80b71` | timeout aplicado às consultas |
| 04/10 | `QA-03/PROJ-43` | `1274a0d` | teste de carga executado |
| 04/10 | `QA-04/PROJ-44` | `569da1f` | resultados e limitações da carga registrados |
| 04/10 | `QA-05/PROJ-45` | `98f891d` | cenários de erro executados |
| 04/10 | `QA-06/PROJ-46` | `49fe3e6` | proteção contra SQL injection validada |
| 06/10 | `LID-03/PROJ-47` | `3acd6e5` | divisão das tasks e histórico de commits consolidados |
| 06/10 | `LID-04/PROJ-48` | `f2faee7` | burndown das duas sprints incluído |
| 09/10 | `LID-05/PROJ-49` | `cc1ebfa` | pontos fortes, fracos, dificuldades e impedimentos registrados |
| 09/10 | `LID-06/PROJ-50` | `e5647e8` | inicialização a partir de clone limpo validada e documentada |
| 09/10 | `LID-07/PROJ-72` | este commit | relatório final revisado e consolidado no formato SBC |

`INF-02/PROJ-4` foi a organização do backlog e do quadro no Jira, sem commit de
código. `LID-07/PROJ-72` identifica o próprio commit que inclui seu registro
nesta tabela; o hash não pode ser autorreferenciado sem alterar novamente o
próprio hash.

#### Marcos

| Data | Task/Jira | Commit | Resultado registrado |
|---|---|---|---|
| 13/09 | `BD-01/PROJ-15` | `1148065` | driver do PostgreSQL adicionado |
| 13/09 | `BD-02/PROJ-16` | `882f94d` | análise inicial dos datasets registrada |
| 14/09 | `BD-03/PROJ-17` | `d64f588` | campos necessários mapeados |
| 15/09 | `BD-04/PROJ-18` | `fe3b0d8` | schema do banco modelado |
| 16/09 | `BD-05/PROJ-19` | `286d627` | tabelas do banco criadas |
| 18/09 | `BD-06/PROJ-20` | `70c9196` | dados preparados para importação |
| 20/09 | `BD-07/PROJ-21` | `d27e820` | dados tratados importados |
| 20/09 | `BD-08/PROJ-22` | `66f5f0b` | índices de busca criados |
| 20/09 | `BACK-01/PROJ-23` | `e4513c3` | esqueleto Flask criado |
| 23/09 | `BACK-02/PROJ-24` | `ccdf5c4` | Gunicorn multithread configurado |
| 23/09 | `BACK-03/PROJ-25` | `4cfa188` | conexão com PostgreSQL criada |
| 23/09 | `BACK-04/PROJ-26` | `70f63a5` | busca exata por nome implementada |
| 26/09 | `BACK-05/PROJ-27` | `8e440b9` | filtros por cargo e UF implementados |
| 26/09 | `BACK-06/PROJ-28` | `47e3872` | filtro por órgão implementado |
| 27/09 | `BACK-07/PROJ-51` | `f8a1064` | busca combinada implementada |
| 30/09 | `BACK-08/PROJ-52` | `ed9e38f` | busca por similaridade implementada |
| 30/09 | `BACK-09/PROJ-53` | `389c272` | paginação dos resultados implementada |
| 30/09 | `BACK-10/PROJ-54` | `728568f` | parâmetros de busca validados |
| 04/10 | `BACK-11/PROJ-55` | `545c692` | cenários de erro tratados |
| 04/10 | `BACK-12/PROJ-56` | `e1d822f` | respostas JSON padronizadas |
| 04/10 | `BD-09/PROJ-57` | `1404a59` | busca por similaridade otimizada |
| 04/10 | `BACK-13/PROJ-58` | `41eb8da` | testes automatizados dos endpoints adicionados |
| 06/10 | `BACK-14/PROJ-59` | `24a866c` | endpoints, parâmetros e exemplos documentados |
| 06/10 | `BACK-15/PROJ-60` | `0a28f98` | respostas de erro da API corrigidas e revalidadas |

#### Alex

| Data | Task/Jira | Commit | Resultado registrado |
|---|---|---|---|
| 13/09 | `FRONT-01/PROJ-29` | `58ffbc9` | estrutura inicial do frontend configurada |
| 13/09 | `FRONT-02/PROJ-30` | `776d42f` | identidade visual definida |
| 14/09 | `FRONT-03/PROJ-31` | `9ab57fe` | layout base criado |
| 15/09 | `FRONT-04/PROJ-32` | `ea59923` | formulário de busca criado |
| 16/09 | `FRONT-05/PROJ-33` | `9febd91` | formulário de busca estilizado |
| 18/09 | `FRONT-06/PROJ-34` | `4123f17` | listagem com registros fictícios criada |
| 18/09 | `FRONT-07/PROJ-35` | `f6a31fd` | listagem de resultados estilizada |
| 20/09 | `FRONT-08/PROJ-36` | `8570123` | paginação com dados fictícios criada |
| 20/09 | `FRONT-09/PROJ-37` | `ad846df` | estados simulados de resultados criados |
| 23/09 | `FRONT-10/PROJ-38` | `44d97f8` | responsividade inicial ajustada |
| 27/09 | `FRONT-11/PROJ-61` | `cc9f180` | frontend integrado à API real |
| 27/09 | `FRONT-12/PROJ-62` | `3703715` | busca exata por nome implementada |
| 30/09 | `FRONT-13/PROJ-63` | `ef2df83` | busca por similaridade implementada |
| 30/09 | `FRONT-14/PROJ-64` | `4b13c89` | filtros individuais implementados |
| 30/09 | `FRONT-15/PROJ-65` | `fb65451` | busca combinada implementada |
| 04/10 | `FRONT-16/PROJ-66` | `a9ed8db` | paginação integrada aos resultados reais |
| 04/10 | `FRONT-17/PROJ-67` | `09b01a6` | resultado único diferenciado da listagem |
| 04/10 | `FRONT-18/PROJ-68` | `982d69a` | feedback real de carregamento e erro adicionado |
| 04/10 | `FRONT-19/PROJ-69` | `70e40cd` | responsividade e apresentação final ajustadas |
| 06/10 | `FRONT-20/PROJ-70` | `6ab7768` | estados de busca e respostas inválidas corrigidos e revalidados |

## 9. Burndown

![Burndown das Sprints 1 e 2](./burndown.svg)

O [gráfico em SVG](./burndown.svg) usa a carga planejada do backlog: 56 Story
Points na Sprint 1 e uma linha-base de 57 na Sprint 2. A inclusão de
`LID-07/PROJ-72` em 09/10 acrescentou 2 pontos e elevou o escopo final da
Sprint 2 para 59. A atividade opcional `BONUS-01` foi excluída porque não faz
parte desses totais e não foi iniciada. A linha ideal usa a linha-base definida
no início de cada sprint. A linha real apresenta o saldo ao fim de cada dia; o
ajuste de escopo de 09/10 é anotado separadamente para não reescrever os saldos
históricos.

### 9.1 Dados da Sprint 1

| Data | Tasks concluídas na data | SP concluídos | SP restantes |
|---|---|---:|---:|
| Início | — | 0 | 56 |
| 12/09 | `PROJ-3` | 1 | 55 |
| 13/09 | `PROJ-4`, `PROJ-15`, `PROJ-16`, `PROJ-29`, `PROJ-30` | 7 | 48 |
| 14/09 | `PROJ-5`, `PROJ-17`, `PROJ-31` | 5 | 43 |
| 15/09 | `PROJ-6`, `PROJ-18`, `PROJ-32` | 5 | 38 |
| 16/09 | `PROJ-7`, `PROJ-19`, `PROJ-33` | 4 | 34 |
| 17/09 | — | 0 | 34 |
| 18/09 | `PROJ-8`, `PROJ-9`, `PROJ-20`, `PROJ-34`, `PROJ-35` | 9 | 25 |
| 19/09 | — | 0 | 25 |
| 20/09 | `PROJ-10`, `PROJ-11`, `PROJ-21`, `PROJ-22`, `PROJ-23`, `PROJ-36`, `PROJ-37` | 11 | 14 |
| 21/09 | — | 0 | 14 |
| 22/09 | — | 0 | 14 |
| 23/09 | `PROJ-12`, `PROJ-14`, `PROJ-24`, `PROJ-25`, `PROJ-26`, `PROJ-38` | 10 | 4 |
| 24/09 | — | 0 | 4 |
| 25/09 | — | 0 | 4 |
| 26/09 | `PROJ-13`, `PROJ-27`, `PROJ-28` | 4 | 0 |

A Sprint 1 consumiu os 56 pontos planejados e encerrou sem saldo em 26/09. Os
trechos horizontais representam dias sem conclusão registrada, não ausência de
trabalho.

### 9.2 Dados da Sprint 2 até 09/10/2026

| Data | Ajuste de escopo | Tasks concluídas na data | SP concluídos | SP restantes ao fim do dia |
|---|---:|---|---:|---:|
| Início | — | — | 0 | 57 |
| 27/09 | — | `PROJ-39`, `PROJ-51`, `PROJ-61`, `PROJ-62` | 8 | 49 |
| 28/09 | — | — | 0 | 49 |
| 29/09 | — | — | 0 | 49 |
| 30/09 | — | `PROJ-40`, `PROJ-41`, `PROJ-42`, `PROJ-52`, `PROJ-53`, `PROJ-54`, `PROJ-63`, `PROJ-64`, `PROJ-65` | 17 | 32 |
| 01/10 | — | — | 0 | 32 |
| 02/10 | — | — | 0 | 32 |
| 03/10 | — | — | 0 | 32 |
| 04/10 | — | `PROJ-43` a `PROJ-46`, `PROJ-55` a `PROJ-58`, `PROJ-66` a `PROJ-69` | 21 | 11 |
| 05/10 | — | — | 0 | 11 |
| 06/10 | — | `PROJ-47`, `PROJ-48`, `PROJ-59`, `PROJ-60`, `PROJ-70` | 8 | 3 |
| 07/10 | — | — | 0 | 3 |
| 08/10 | — | — | 0 | 3 |
| 09/10 | +2 (`PROJ-72`) | `PROJ-49`, `PROJ-50`, `PROJ-72` | 5 | 0 |
| 10–11/10 | — | período posterior ao fechamento | — | 0 |

A Sprint 2 iniciou com 57 pontos e terminou com escopo final de 59 pontos. Em
09/10 havia 3 pontos restantes, foram adicionados 2 pontos de `LID-07/PROJ-72`
e os 5 pontos foram concluídos. As quedas concentradas em 30/09, 04/10 e 06/10
refletem a integração em lotes. O backlog obrigatório foi encerrado dois dias
antes do fim do período.

## 10. Estratégia e resultados dos testes

| Verificação | Resultado |
|---|---|
| Testes automatizados do backend | 12 de 12 aprovados |
| Cenários funcionais e de erro contra Flask/Gunicorn e PostgreSQL reais | 20 de 20 aprovados |
| Tentativas de SQL injection | 45 de 45 aprovadas, sem alteração das tabelas, contagens ou fingerprints |
| Carga de capacidade | 20 requisições, concorrência 2, todas HTTP 200, sem erro de transporte |
| Sobrecarga | 200 requisições, concorrência 32; 2 HTTP 200 e 198 HTTP 429, sem erro de transporte |
| Disponibilidade após a sobrecarga | `/health` respondeu HTTP 200 |
| Timeout real | Consulta bloqueada retornou HTTP 504 em aproximadamente 2 segundos |
| Clone limpo | Três imagens construídas, banco e backend saudáveis, frontend e `/health` com HTTP 200 |
| Integração do frontend no clone limpo | Busca percorreu frontend, proxy e API e apresentou corretamente o estado sem resultados |

A bateria funcional cobriu filtro vazio, espaços, tentativa representativa de
injeção, nome inexistente, múltiplos resultados paginados, cargo inválido, UF
inválida, órgão inválido, rota e página inexistentes, parâmetro desconhecido,
limites inválidos, combinação inválida, timeout, concorrência e disponibilidade
posterior.

Na bateria de segurança, os payloads foram enviados aos filtros de nome, cargo,
UF, órgão e similaridade. As quatro tabelas permaneceram existentes, e suas
contagens e fingerprints permaneceram idênticas antes e depois dos 45 casos.

Não houve cenário reprovado ou bloqueado nas evidências persistidas. Não foram
executados teste prolongado de estabilidade, distribuição entre múltiplas
instâncias, medição de desempenho com o conjunto público completo nem o
aplicativo desktop opcional. Também não há artefato versionado com uma bateria
manual completa do frontend; a evidência persistida comprova o build, o
carregamento da interface e o caminho integrado do estado sem resultados.

### 10.1 Validação a partir de clone limpo

Em 09/10/2026, a aplicação foi clonada para um diretório temporário novo. O
clone não continha `.env` nem arquivos não versionados, e o projeto isolado do
Compose não reutilizou volumes anteriores. A composição passou a fornecer
valores locais padrão para conexão entre os serviços, preservando a
possibilidade de substituí-los por variáveis externas.

O comando executado foi:

```powershell
docker compose up --build --detach --wait
```

As três imagens foram construídas sem alteração manual. O PostgreSQL e o
backend atingiram o estado saudável, o frontend permaneceu em execução e a
interface respondeu HTTP 200. O endpoint `/health` respondeu HTTP 200 com o
envelope JSON esperado. Os 12 testes automatizados do backend também passaram.

O banco criado no clone continha as quatro tabelas do schema e nenhum servidor,
pois os dados públicos não são versionados no repositório. Uma busca pela
interface percorreu o proxy e a API e apresentou o estado sem resultados; a
requisição correspondente retornou HTTP 404 em JSON de forma controlada. A
validação comprova a inicialização autossuficiente e o funcionamento da
aplicação com a base vazia, mas não representa uma busca positiva no conjunto
público.

## 11. Pontos fortes da equipe

- A divisão por área permaneceu estável: Pedro concentrou infraestrutura, QA e
  gestão; Marcos, banco de dados e backend; e Alex, frontend. O histórico de
  commits preservou essa autoria e permitiu conferir cada entrega por
  responsável.
- A equipe concluiu os 56 Story Points da Sprint 1 e os 59 Story Points da
  Sprint 2. Os lotes mantiveram commits separados por task, mesmo quando duas
  atividades relacionadas compartilharam a mesma integração.
- As validações produziram evidências reproduzíveis. Em 04/10, os 20 cenários
  funcionais e de erro e as 45 tentativas de SQL injection foram aprovados; os
  testes de carga também demonstraram que o excesso de requisições era
  rejeitado de forma controlada, sem indisponibilizar o serviço.
- Os problemas encontrados pelo QA geraram correções no backend e no frontend.
  Entre elas estão a padronização das respostas de erro em JSON, o bloqueio de
  buscas sem filtro e o tratamento visual de buscas vazias ou de respostas
  inválidas.

## 12. Pontos fracos

- A cadência não foi uniforme. Houve dias sem entrega integrada e quedas
  concentradas no burndown em 20/09, 23/09, 30/09, 04/10 e 06/10, o que reduziu
  a visibilidade diária do avanço, embora as tasks continuassem identificadas
  separadamente.
- A capacidade do backend ficou limitada a duas buscas simultâneas. No cenário
  de sobrecarga, 198 de 200 requisições foram rejeitadas com HTTP 429; o
  comportamento preservou a aplicação, mas evidencia baixa capacidade para
  picos de acesso.
- Os testes de desempenho foram locais, com uma única instância do backend e
  100.000 registros sintéticos. A equipe não mediu estabilidade prolongada,
  distribuição entre instâncias nem o conjunto público completo, portanto os
  resultados não representam diretamente um ambiente de produção.
- A documentação final foi consolidada perto do encerramento da Sprint 2. Isso
  aumentou a quantidade de informações que precisaram ser conferidas de uma só
  vez a partir do board, do acompanhamento e do histórico Git.

## 13. Dificuldades e impedimentos

| Período | Dificuldade ou impedimento | Ação e resultado |
|---|---|---|
| 12/09 | A estrutura inicial não correspondia à convenção definida para a raiz do projeto. | `backend`, `frontend`, `db` e a composição foram mantidos diretamente na raiz antes da continuidade das demais tasks. |
| 13/09 | Os três integrantes trabalhavam no mesmo computador e precisavam manter identidades distintas. | Foram usados clones e configurações de identidade separados, preservando a autoria dos commits de Pedro, Marcos e Alex. |
| 15/09 | A validação das imagens dependia do Docker em execução. | O ambiente foi inicializado antes das verificações e essa dependência passou a ser considerada na preparação das execuções seguintes. |
| 17 a 25/09 | Interrupções e dias sem integração acumularam entregas da Sprint 1. | As mudanças foram retomadas em lotes, mantendo commits atômicos e a identificação de cada task; a sprint encerrou em 26/09 com 56 de 56 pontos. |
| 04/10 | Os testes de carga confirmaram a baixa capacidade para acessos simultâneos e o custo elevado da busca ampla por similaridade. | O limite de duas buscas configurado em 30/09 fez o excesso falhar de forma controlada com HTTP 429; o timeout permaneceu como proteção para consultas longas, e a busca por similaridade recebeu o ajuste de índice previsto em `BD-09/PROJ-57`. |

Os dias sem entrega integrada foram mantidos explicitamente no acompanhamento e
no burndown. Eles não foram convertidos em trabalho presumido nem em resultados
de teste não executados.

## 14. Limitações conhecidas

- A medição foi feita localmente, em containers, com 100.000 registros sintéticos e sem latência de rede externa. Os números não representam diretamente a base pública completa nem um ambiente de produção.
- O limite de duas buscas simultâneas preservou a disponibilidade, mas rejeitou 198 de 200 requisições no cenário com concorrência 32. A vazão total de 436,52 respostas por segundo nesse cenário representa principalmente rejeições HTTP 429; a vazão observada de buscas concluídas foi 6,85 requisições por segundo no cenário com concorrência 2.
- A consulta ampla por similaridade usada no teste correspondeu aos 100.000 registros. O plano de execução fez varredura sequencial da tabela, calculou similaridade para todos os resultados e aplicou ordenação `top-N`; isoladamente, essa consulta levou 294,303 ms. Esse ponto deve orientar a avaliação de índices e seletividade em BD-09/PROJ-57 com a base representativa.
- Não foram executados teste prolongado de estabilidade, distribuição entre múltiplas instâncias ou medição com o conjunto público completo.

## 15. Conclusão

O projeto entregou a aplicação web modularizada em três serviços, com
PostgreSQL, API Flask executada pelo Gunicorn e frontend React integrado por
HTTP. Foram implementadas buscas por nome exato, similaridade, cargo, UF, órgão
e combinações de filtros, além de paginação e apresentação diferenciada para
um ou vários resultados.

A API possui respostas JSON padronizadas, validação de entrada, consultas
parametrizadas, limite de concorrência, timeout e tratamento dos erros previstos
no enunciado. Os testes automatizados, funcionais, de segurança, carga e
inicialização em clone limpo foram concluídos sem reprovações registradas.

Com a conclusão de `LID-07/PROJ-72`, a Sprint 1 encerra com 56 de 56 pontos e a
Sprint 2 com 59 de 59 pontos. Não restam atividades obrigatórias do backlog. O
aplicativo desktop não foi desenvolvido, pois corresponde ao item adicional da
avaliação.

Os arquivos públicos do banco não são versionados. Um clone limpo cria o schema
e inicia todos os serviços, mas permanece sem registros até a execução do
tratamento e da importação. Também permanecem como limitações os testes
exclusivamente locais, a capacidade de duas buscas simultâneas e a ausência de
testes prolongados ou distribuídos.

## 16. Evidências e referências

### 16.1 Fontes públicas

- [Portal Brasileiro de Dados Abertos - Gestão de Pessoas do Executivo Federal - Aposentados](https://dados.gov.br/dados/conjuntos-dados/gestao-de-pessoas-executivo-federal--aposentados)
- [Portal Brasileiro de Dados Abertos - Gestão de Pessoas do Executivo Federal - Carreiras/Cargos](https://dados.gov.br/dados/conjuntos-dados/gestao-de-pessoas-executivo-federal---carreiras--cargos)
- [Dicionário de dados de Aposentados](http://repositorio.dados.gov.br/segrt/1.20180829-DadosRecursos-Aposentados.pdf)
- [Dicionário de dados de Carreiras/Cargos](http://repositorio.dados.gov.br/segrt/2.20190709-DadosRecursos-Carreiras.pdf)

### 16.2 Documentação do projeto

- `docs/analise-datasets.md`: disponibilidade, volume e estrutura das fontes;
- `docs/mapeamento-campos.md`: correspondência entre os campos da aplicação e
  os dicionários oficiais;
- `docs/modelo-banco.md`: modelo conceitual, estrutura lógica e relacionamentos;
- `backend/README.md`: endpoints, parâmetros, exemplos e códigos de resposta;
- `docs/plano-testes.md`: cenários funcionais e de erro;
- `docs/casos-sql-injection.md`: payloads e matriz de segurança;
- `docs/validacao-compose.md`: validação inicial dos serviços e da rede interna;
- `docs/acompanhamento-sprint-1.md`: acompanhamento e impedimentos;
- `docs/burndown.svg`: evolução dos Story Points;
- histórico Git: autoria, datas e mensagens dos commits.

### 16.3 Evidências executadas

- `docs/evidencias/validacao-api-2026-10-04.json`: 20 cenários funcionais e de
  erro;
- `docs/evidencias/sql-injection-2026-10-04.json`: 45 casos de SQL injection e
  integridade do banco;
- `docs/evidencias/teste-carga-capacidade-2026-10-04.json`: carga com
  concorrência 2;
- `docs/evidencias/teste-carga-2026-10-04.json`: sobrecarga com concorrência 32;
- Seção 10.1 deste relatório: construção e execução a partir de clone limpo.
