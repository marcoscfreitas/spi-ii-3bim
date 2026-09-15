const fieldClassName =
  'mt-2 w-full rounded-md border border-border bg-surface px-3 py-2 text-body'

const estados = [
  'AC',
  'AL',
  'AP',
  'AM',
  'BA',
  'CE',
  'DF',
  'ES',
  'GO',
  'MA',
  'MT',
  'MS',
  'MG',
  'PA',
  'PB',
  'PR',
  'PE',
  'PI',
  'RJ',
  'RN',
  'RS',
  'RO',
  'RR',
  'SC',
  'SP',
  'SE',
  'TO',
]

export function SearchForm() {
  return (
    <form aria-label="Filtros de busca" className="mt-8 grid gap-5 md:grid-cols-2">
      <label className="font-medium text-body">
        Nome
        <input
          className={fieldClassName}
          name="nome"
          placeholder="Digite o nome"
          type="text"
        />
      </label>

      <label className="font-medium text-body">
        Cargo
        <input
          className={fieldClassName}
          name="cargo"
          placeholder="Digite o cargo"
          type="text"
        />
      </label>

      <label className="font-medium text-body">
        UF
        <select className={fieldClassName} defaultValue="" name="uf">
          <option value="">Selecione a UF</option>
          {estados.map((estado) => (
            <option key={estado} value={estado}>
              {estado}
            </option>
          ))}
        </select>
      </label>

      <label className="font-medium text-body">
        Órgão
        <input
          className={fieldClassName}
          name="orgao"
          placeholder="Digite o órgão"
          type="text"
        />
      </label>
    </form>
  )
}
