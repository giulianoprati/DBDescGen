import os
from llama_index.llms.dashscope import DashScope, DashScopeGenerationModels
from sqlalchemy import create_engine
from schema_engine import SchemaEngine

dashscope_llm = DashScope(model_name=DashScopeGenerationModels.QWEN_PLUS, api_key='YOUR API KEY HERE.')

db_path = './book_1.sqlite'
db_abs_path = os.path.abspath(db_path)
db_engine = create_engine(f'sqlite:///{db_abs_path}')

comment_mode = 'generation'
schema_engine_instance = SchemaEngine(db_engine, llm=dashscope_llm, db_name='book_1',
                                      comment_mode=comment_mode)
schema_engine_instance.fields_category()
schema_engine_instance.table_and_column_desc_generation()
mschema = schema_engine_instance.mschema
mschema.save('./book_1.json')
mschema_str = mschema.to_mschema()
print(mschema_str)