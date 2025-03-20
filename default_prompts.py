from llama_index.core.prompts import PromptTemplate
from llama_index.core.prompts.prompt_type import PromptType

DEFAULT_IS_DATE_TIME_FIELD_TMPL = """You are now a data analyst. Given information about a column in a data table, please analyze whether this column represents a datetime type. Answer only "Yes" or "No".
A datetime type is defined as a combination of one or more of the following: year, month, day, hour, minute, and second, with the constraints that the month must be between 1 and 12, the day between 1 and 31, the hour between 0 and 23, and the minute and second between 0 and 59.

{field_info_str}
"""

DEFAULT_IS_DATE_TIME_FIELD_PROMPT = PromptTemplate(
    DEFAULT_IS_DATE_TIME_FIELD_TMPL,
    prompt_type=PromptType.CUSTOM,
)

DEFAULT_DATE_TIME_MIN_GRAN_TMPL = """You are now a data analyst. Given a column from a data table that represents time or date information, please infer the minimum granularity of the column based on its format and sample data.
Note: The minimum granularity of a datetime field refers to the smallest time unit that the column can accurately represent.

Below are the common time units:
YEAR: The smallest time unit is a year, e.g., 2024
MONTH: The month of a year; there are 12 months, with values from 1 to 12, e.g., 2024-12
DAY: The day of the month; a month can have at most 31 days, so values range from 1 to 31, e.g., 2024-12-31
WEEK: Calendar week; generally the week number in a year. A year typically has 52 weeks (plus a few days), with week numbers usually ranging from 0 to 53, e.g., 2024-34
QUARTER: The quarter of a year; a year has four quarters, typically numbered from 1 to 4
HOUR: The hour of the day; there are 24 hours in a day, with values from 0 to 23
MINUTE: The minute within an hour; there are 60 minutes in an hour, with values from 0 to 59
SECOND: The second within a minute; there are 60 seconds in a minute, with values from 0 to 59
MILLISECOND: Millisecond
MICROSECOND: Microsecond
OTHER: Any other time unit not listed above, such as half a year or a quarter-hour

Directly provide the name of the smallest time unit.

Here are some examples for your reference:
[Column Information]
Column Name: dt
Data Type: DOUBLE
Value Examples: [202412.0, 202301.0, 202411.0, 202201.0, 202308.0, 202110.0, 202211.0]
Minimum Time Unit: MONTH

[Column Information]
Column Name: dt
Data Type: TEXT
Value Examples: ['2022-12', '2022-14', '2021-40', '2021-37', '2021-01', '2021-32', '2023-04', '2023-37']
Minimum Time Unit: WEEK

[Column Information]
Column Name: dt
Data Type: TEXT
Value Examples: ['12:30:30', '23:45:23', '01:23:12', '12:12:12', '14:34:31', '18:43:01', '22:13:21']
Minimum Time Unit: SECOND

Please refer to the examples above and deduce the minimum time unit for the following column. Directly provide the name of the smallest time unit.
[Column Information]
{field_info_str}
Minimum Time Unit: """

DEFAULT_DATE_TIME_MIN_GRAN_PROMPT = PromptTemplate(
    DEFAULT_DATE_TIME_MIN_GRAN_TMPL,
    prompt_type=PromptType.CUSTOM,
)

DEFAULT_STRING_CATEGORY_FIELD_TMPL = '''You are now a data analyst. Given information about a column in a data table, please determine whether the column is of type enum, code, or text. Answer only "enum", "code", or "text".

enum: Has the characteristics of an enumeration, meaning the column values are relatively fixed and belong to a predefined limited set, usually short and following a consistent pattern, typically used for statuses or types.
code: A code with specific meaning; its composition usually follows certain rules or standards, such as user IDs or identity card numbers.
text: Free text, usually used for descriptions or explanations, with no constraints on length or format; it can be any form of text.

{field_info_str}
'''

DEFAULT_STRING_CATEGORY_FIELD_PROMPT = PromptTemplate(
    DEFAULT_STRING_CATEGORY_FIELD_TMPL,
    prompt_type=PromptType.CUSTOM,
)

DEFAULT_NUMBER_CATEGORY_FIELD_TMPL = """You are now a data analyst. Given information about a column in a data table, please determine whether the column is of type enum, code, or measure. Answer only "enum", "code", or "measure".

enum: Enumeration type, where the values are confined to a predefined limited set, usually short and typically used for statuses or types.
code: A code with specific meaning; its composition usually follows certain rules or standards, such as user IDs or identity card numbers.
measure: A metric or measure that can be used for computations and aggregations, such as calculating averages or maximum values.

{field_info_str}
"""

DEFAULT_NUMBER_CATEGORY_FIELD_PROMPT = PromptTemplate(
    DEFAULT_NUMBER_CATEGORY_FIELD_TMPL,
    prompt_type=PromptType.CUSTOM,
)

DEFAULT_UNKNOWN_CATEGORY_FIELD_TMPL = """You are now a data analyst. Given information about a column in a data table, please determine whether the column is of type enum, measure, code, or text. Answer only "enum", "measure", "code", or "text".

enum: Enumeration type, where the values are confined to a predefined limited set, usually short and typically used for statuses or types.
code: A code with specific meaning; its composition usually follows certain rules or standards, such as user IDs or identity card numbers.
text: Free text, usually used for descriptions or explanations, with no restrictions on length; it can be any form of text.
measure: A metric or measure that can be used for computations and aggregations, such as calculating averages or maximum values.

{field_info_str}
"""

DEFAULT_UNKNOWN_FIELD_PROMPT = PromptTemplate(
    DEFAULT_UNKNOWN_CATEGORY_FIELD_TMPL,
    prompt_type=PromptType.CUSTOM,
)

DEFAULT_COLUMN_DESC_GEN_CHINESE_TMPL = '''You are now a data analyst. Here is the column information and some sample data for a data table:

{table_mschema}

[SQL]
{sql}
[Examples]
{sql_res}

Below are the details of the column "{field_name}" in the table:
{field_info_str}

The following information is provided for your reference:
{supp_info}

Now, please carefully read and understand the above content and data, and add an italian name for the column "{field_name}" with the following requirements:
1. The Italian name should be as concise and clear as possible, accurately describing the business meaning of the column without deviating from its original description.
2. The Italian name must not exceed 20 characters.
3. Output your answer in JSON format:
```json
{"chinese_name": ""}
```
'''

DEFAULT_COLUMN_DESC_GEN_CHINESE_PROMPT = PromptTemplate(
    DEFAULT_COLUMN_DESC_GEN_CHINESE_TMPL,
    prompt_type=PromptType.CUSTOM,
)

DEFAULT_COLUMN_DESC_GEN_ENGLISH_TMPL = '''You are now a data analyst. Here is the column information and some sample data for a data table:

{table_mschema}

[SQL]
{sql}
[Examples]
{sql_res}

Below are the details of the column "{field_name}" in the table:
{field_info_str}

The following information is provided for your reference:
{supp_info}

Now, please carefully read and understand the above content and data, and add an English description for the column "{field_name}" with the following requirements:
1. The English description should be as concise and clear as possible, accurately describing the business meaning of the column without deviating from its original description.
2. The total output length should not exceed 20 words.
3. Output your answer in JSON format:
```json
{"english_desc": ""}
```
'''

DEFAULT_COLUMN_DESC_GEN_ENGLISH_PROMPT = PromptTemplate(
    DEFAULT_COLUMN_DESC_GEN_ENGLISH_TMPL,
    prompt_type=PromptType.CUSTOM,
)


DEFAULT_UNDERSTAND_DATABASE_TMPL = '''You are now a data analyst. Here is the schema of a database:

{db_mschema}

Please carefully read the above information and analyze, at the database level, what domain and type of data the database primarily stores. Provide a summary only; there is no need to analyze each table individually.
'''

DEFAULT_UNDERSTAND_DATABASE_PROMPT = PromptTemplate(
    DEFAULT_UNDERSTAND_DATABASE_TMPL,
    prompt_type=PromptType.CUSTOM,
)

DEFAULT_GET_DOMAIN_KNOWLEDGE_TMPL = '''There is a database with the following basic information:
{db_info}

Based on your knowledge, please analyze what dimensions and metrics are typically of interest in this domain.
'''

DEFAULT_GET_DOMAIN_KNOWLEDGE_PROMPT = PromptTemplate(
    DEFAULT_GET_DOMAIN_KNOWLEDGE_TMPL,
    prompt_type=PromptType.CUSTOM,
)

# Understanding the differences and relationships between fields based on their category
DEFAULT_UNDERSTAND_FIELDS_BY_CATEGORY_TMPL = '''You are now a data analyst. Here is the basic information of a dataset:

[Database Information]
{db_info}

For the data table "{table_name}", the column information and sample data are as follows:
{table_mschema}

[SQL]
{sql}
[Examples]
{sql_res}

Please carefully read and understand the data table. Knowing that the fields {fields} in the table are all of type {category}, please analyze the relationships and differences among these fields.
'''

DEFAULT_UNDERSTAND_FIELDS_BY_CATEGORY_PROMPT = PromptTemplate(
    DEFAULT_UNDERSTAND_FIELDS_BY_CATEGORY_TMPL,
    prompt_type=PromptType.CUSTOM,
)

DEFAULT_TABLE_DESC_GEN_CHINESE_TMPL = '''You are now a data analyst. Here is the column information for a data table:

{table_mschema}

Below are some sample data:
[SQL]
{sql}
[Examples]
{sql_res}

Now, please carefully read and understand the above content and data, and generate a table description in Italian for the data table with the following requirements:
1. Describe which dimensions (including time dimensions and other dimensions) and what metrics data the table stores.
2. The description should be no longer than 100 Italian characters.
3. Provide your answer in JSON format.

```json
{"table_desc": ""}
```
'''

DEFAULT_TABLE_DESC_GEN_CHINESE_PROMPT = PromptTemplate(
    DEFAULT_TABLE_DESC_GEN_CHINESE_TMPL,
    prompt_type=PromptType.CUSTOM,
)

DEFAULT_TABLE_DESC_GEN_ENGLISH_TMPL = '''You are now a data analyst. Here is the column information for a data table:

{table_mschema}

Below are some sample data:
[SQL]
{sql}
[Examples]
{sql_res}

Now, please carefully read and understand the above content and data, and generate an English table description for the data table with the following requirements:
1. Describe which dimensions (including time dimensions and other dimensions) and what metrics data the table stores.
2. The description should not exceed 100 words.
3. Provide your answer in JSON format.

```json
{"table_desc": ""}
```
'''

DEFAULT_TABLE_DESC_GEN_ENGLISH_PROMPT = PromptTemplate(
    DEFAULT_TABLE_DESC_GEN_ENGLISH_TMPL,
    prompt_type=PromptType.CUSTOM,
)

DEFAULT_SQL_GEN_TMPL = '''You are now a {dialect} data analyst. Here is the schema information of a database:

[Database Schema]
{db_mschema}

[User Question]
{question}
[Reference Information]
{evidence}

Please carefully read and understand the database. Based on the user's question and the provided reference information, generate an executable SQL query to answer the user's question. Enclose the generated SQL within ```sql and ```.
'''

DEFAULT_SQL_GEN_PROMPT = PromptTemplate(
    DEFAULT_SQL_GEN_TMPL,
    prompt_type=PromptType.CUSTOM,
)


