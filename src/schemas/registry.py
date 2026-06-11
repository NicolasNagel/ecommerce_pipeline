import pandera.pandas as pa
import yaml

from pathlib import Path


class SchemaRegistry:
    """
    Carrega e armazena contratos de schema a partir de arquivos YAML.

    Responsabilidades:
        - Localizar arquivo YAML pelo nome do dataset;
        - Construir o schema pandera apartir do YAML;
        - Cachear schemas já carregados para evitar releitura.
    """
    TYPE_MAP = {
        "int64": pa.Int64,
        "float64": pa.Float64,
        "string": pa.String,
        "bool": pa.Bool,
        "datetime64[ns]": pa.DateTime
    }

    def __init__(self, schema_dir: str | Path = 'src/schemas/contracts') -> None:
        self.schema_dir = Path(schema_dir)
        self._cache: dict[str, pa.DataFrameSchema] = {}

    def get(self, dataset_name: str) -> pa.DataFrameSchema | None:
        if dataset_name in self._cache:
            return self._cache[dataset_name]
        
        schema_path = self.schema_dir / f'{dataset_name}.yaml'
        if not schema_path.exists():
            return None
        
        with open(schema_path, encoding='utf-8') as file:
            raw = yaml.safe_load(file)

        columns = {
            col: pa.Column(
                dtype=self.TYPE_MAP[props['type']],
                nullable=props.get('nullable', True)
            )
            for col, props in raw['columns'].items()
        }

        schema = pa.DataFrameSchema(
            columns=columns,
            strict=True
        )

        self._cache[dataset_name] = schema
        return schema