const resultadosMockados = [
  {
    id: 1,
    nome: 'Pessoa Exemplo 1',
    cargo: 'Analista administrativo',
    uf: 'DF',
    orgao: 'Órgão Exemplo A',
  },
  {
    id: 2,
    nome: 'Pessoa Exemplo 2',
    cargo: 'Técnico em assuntos educacionais',
    uf: 'SP',
    orgao: 'Órgão Exemplo B',
  },
  {
    id: 3,
    nome: 'Pessoa Exemplo 3',
    cargo: 'Assistente em administração',
    uf: 'RJ',
    orgao: 'Órgão Exemplo C',
  },
]

export function ResultsList() {
  return (
    <section aria-labelledby="results-title">
      <h2 id="results-title">Resultados de exemplo</h2>
      <p>Os registros abaixo são fictícios.</p>
      <ul>
        {resultadosMockados.map((resultado) => (
          <li key={resultado.id}>
            <h3>{resultado.nome}</h3>
            <dl>
              <div>
                <dt>Cargo</dt>
                <dd>{resultado.cargo}</dd>
              </div>
              <div>
                <dt>UF</dt>
                <dd>{resultado.uf}</dd>
              </div>
              <div>
                <dt>Órgão</dt>
                <dd>{resultado.orgao}</dd>
              </div>
            </dl>
          </li>
        ))}
      </ul>
    </section>
  )
}
