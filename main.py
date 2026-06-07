from src.pipeline.pipeline_runner import PipelineRunner
from src.core.settings import settings


if __name__ == '__main__':
    pipeline = PipelineRunner(
        source_dir='src/data',
        container_name='datalake',
        root_folder='staging',
        db_connection_string=settings.database_url,
        db_schema='bronze'
    )

    pipeline.run()