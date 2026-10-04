# Relatório final do projeto

> Documento-base. As seções marcadas como pendentes serão consolidadas no fechamento do projeto com dados verificados das duas sprints.

## 1. Identificação

- Disciplina: [preencher]
- Turma: [preencher]
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

No fechamento, esta seção deve relacionar cada integrante às tasks efetivamente concluídas nas duas sprints.

## 4. Metodologia e organização das sprints

Descrever:

- organização do backlog e do quadro Kanban;
- duração e objetivo de cada sprint;
- critérios de priorização e Story Points;
- fluxo de branches, commits e Pull Requests;
- forma de acompanhamento diário.

## 5. Arquitetura e execução

Documentar:

- containers de PostgreSQL, backend e frontend;
- comunicação entre os serviços;
- tecnologias utilizadas;
- estrutura das principais pastas;
- comando de inicialização a partir da raiz;
- variáveis de ambiente necessárias, sem expor credenciais.

## 6. Tratamento e organização dos dados

Registrar:

- fontes públicas utilizadas;
- campos selecionados a partir dos dicionários;
- limpeza e tratamento realizados;
- modelo relacional e importação;
- contagens reconciliadas;
- índices e busca por similaridade.

## 7. Funcionalidades implementadas

### 7.1 Backend

[Preencher no fechamento com os endpoints e comportamentos realmente validados.]

### 7.2 Frontend

[Preencher no fechamento com as buscas, paginação e estados realmente integrados à API.]

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

Incluir uma tabela com:

| Data | Integrante | Task/Jira | Commit | Resultado |
|---|---|---|---|---|
| [preencher] | [preencher] | [preencher] | [preencher] | [preencher] |

O acompanhamento da primeira sprint está iniciado em [acompanhamento-sprint-1.md](./acompanhamento-sprint-1.md).

## 9. Burndown

[Inserir o gráfico consolidado e explicar desvios entre Story Points planejados e concluídos.]

## 10. Estratégia e resultados dos testes

Consolidar:

- testes funcionais da API;
- entradas inválidas e páginas inexistentes;
- SQL injection;
- timeout;
- carga e requisições simultâneas;
- builds e inicialização dos containers;
- testes manuais do frontend.

Separar resultados aprovados, reprovados, bloqueados e não executados.

## 11. Pontos fortes da equipe

[Preencher com evidências observadas durante as duas sprints.]

## 12. Pontos fracos

[Preencher com evidências observadas durante as duas sprints.]

## 13. Dificuldades e impedimentos

[Consolidar os registros diários e explicar as ações tomadas para cada impedimento.]

## 14. Limitações conhecidas

- A medição foi feita localmente, em containers, com 100.000 registros sintéticos e sem latência de rede externa. Os números não representam diretamente a base pública completa nem um ambiente de produção.
- O limite de duas buscas simultâneas preservou a disponibilidade, mas rejeitou 198 de 200 requisições no cenário com concorrência 32. A vazão total de 436,52 respostas por segundo nesse cenário representa principalmente rejeições HTTP 429; a vazão observada de buscas concluídas foi 6,85 requisições por segundo no cenário com concorrência 2.
- A consulta ampla por similaridade usada no teste correspondeu aos 100.000 registros. O plano de execução fez varredura sequencial da tabela, calculou similaridade para todos os resultados e aplicou ordenação `top-N`; isoladamente, essa consulta levou 294,303 ms. Esse ponto deve orientar a avaliação de índices e seletividade em BD-09/PROJ-57 com a base representativa.
- Não foram executados teste prolongado de estabilidade, distribuição entre múltiplas instâncias ou medição com o conjunto público completo.

## 15. Conclusão

[Resumir o resultado final, os requisitos atendidos e os trabalhos que permaneceram pendentes.]

## 16. Evidências e referências

Relacionar documentação, capturas, logs de testes, fontes oficiais dos dados e demais evidências usadas no relatório.
