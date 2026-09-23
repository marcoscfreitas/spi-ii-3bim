from flask import Flask, jsonify, request

from database import get_connection


app = Flask(__name__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/servidores")
def search_servers_by_name():
    name = request.args.get("nome")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT servidor.id,
                       servidor.nome,
                       cargo.descricao,
                       servidor.uf_sigla,
                       orgao.nome
                FROM servidor
                JOIN cargo ON cargo.id = servidor.cargo_id
                JOIN orgao ON orgao.id = servidor.orgao_id
                WHERE servidor.nome = %s
                ORDER BY servidor.id
                """,
                (name,),
            )
            servers = cursor.fetchall()

    return jsonify(
        [
            {"id": id_, "nome": name, "cargo": role, "uf": state, "orgao": agency}
            for id_, name, role, state, agency in servers
        ]
    )


if __name__ == "__main__":
    app.run()
