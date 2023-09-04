# Filterable

O Filterable é uma biblioteca Python que simplifica a aplicação de filtros e classificações em consultas SQLAlchemy com base em solicitações HTTP. Ele oferece uma maneira conveniente de processar os parâmetros da solicitação e aplicar esses filtros e classificações às consultas SQLAlchemy.

## Instalação

Você pode instalar o Filterable via pip:

```bash
pip install filterable
```

## Exemplo de Uso

Aqui está um exemplo de como  aplicar filtros em suas requests utilizando o Filterable:

```python
from filterable import Filterable
from seu_app.models import UsuarioModel

class SeuController():

    @Filterable(UsuarioModel)
    def get_usuarios(self, _filtered):
        session = Session()
        events_query = self.session.query(Event).filter(
            _filtered.filter
        ).order_by(*_filtered.sort)

        return self.paginate(events_query), 200

``````