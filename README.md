# Automatic database description generation for Text-to-SQL
## Introduction

Supported dialects: SQLite, MySQL and PostgreSQL.

## Requirements
+ python >= 3.9

You can install the required packages with the following command:
```shell
pip install -r requirements.txt
```

## Quick Start

1. Create a database connection.

Connect to SQLite:
```python
import os
db_path = ""
abs_path = os.path.abspath(db_path)
db_engine = create_engine(f'sqlite:///{abs_path}')
```

2. Set llama-index LLM.

Take dashscope as an example:
```python
dashscope_llm = DashScope(model_name=DashScopeGenerationModels.QWEN_PLUS, api_key='YOUR API KEY HERE.')
```

3. Description generation.
```python
comment_mode = 'generation'
schema_engine_instance = SchemaEngine(db_engine, llm=dashscope_llm, db_name='book_1',
                                      comment_mode=comment_mode)
schema_engine_instance.fields_category()
schema_engine_instance.table_and_column_desc_generation()
mschema = schema_engine_instance.mschema
mschema.save('./mschema.json')
mschema_str = mschema.to_mschema()
print(mschema_str)
```

## Citation

```bibtex
@article{gao2025automaticdatabasedescriptiongeneration,
      title={Automatic database description generation for Text-to-SQL}, 
      author={Yingqi Gao and Zhiling Luo},
      year={2025},
      eprint={2502.20657},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2502.20657}, 
}

@article{xiyansql,
      title={A Preview of XiYan-SQL: A Multi-Generator Ensemble Framework for Text-to-SQL}, 
      author={Yingqi Gao and Yifu Liu and Xiaoxia Li and Xiaorong Shi and Yin Zhu and Yiming Wang and Shiqi Li and Wei Li and Yuntao Hong and Zhiling Luo and Jinyang Gao and Liyu Mou and Yu Li},
      year={2024},
      journal={arXiv preprint arXiv:2411.08599},
      url={https://arxiv.org/abs/2411.08599},
      primaryClass={cs.AI}
}
```
