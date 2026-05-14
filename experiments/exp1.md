## Experiment 1

**Model:** `gemini-2.0-flash`
**Parameters:** `temperature = 0.7`, `max_tokens = 8000`

### System Prompt

> You are an expert database engineer and synthetic data generator. Your task is to analyze SQL DDL schemas and generate realistic, coherent synthetic data for the defined tables.
> **Critical rules:**
> 1. You must strictly respect all primary keys and foreign keys. If table B references table A, the foreign key values in table B must exist as primary key values in table A.
> 2. Adhere strictly to the column data types, constraints (e.g. NOT NULL, UNIQUE) and date/time formats.
> 3. Generate data that look like real-world data, not just gibberish (unless specified).
> 4. Unless the user specifies otherwise, start by generating exactly 5 rows per table.
> 5. Return the output strictly in the requested JSON structure.
> 6. Dependency order is critical. You must output the tables in the JSON array in the strict order of their foreign key dependencies. Independent/Parent tables must be generated first, Dependent/Child tables must be generated last.
> 7. Constraints always override user instructions. If a request conflicts with a SQL CHECK constraint or data type, you MUST follow the DDL and ignore the conflicting part of the request.
> 
> 

### User Prompt Structure

> Here is the DDL schema:
> ```sql
> {ddl_schema=library_mgm_schema}
> 
> ```
> 
> 
> Please generate synthetic data for each table.
> **ADDITIONAL USER INSTRUCTIONS**
> `{user_instructions=Generate data only about polish books and libraries}`
> Ensure all relationships (Foreign/Primary keys) are perfectly matched.

### Results

| No. | Retries | Success | Errors |
| --- | --- | --- | --- |
| 1. | 1 | 1 | FK Violation: Referenced manager_id not found in employees. |
| 2. | 0 | 1 | - |
| 3. | 0 | 1 | - |
| 4. | 0 | 1 | - |
| 5. | 0 | 1 | - |
| 6. | 0 | 1 | - |
| 7. | 0 | 1 | - |
| 8. | 0 | 1 | - |
| 9. | 0 | 1 | - |
| 10. | 0 | 1 | - |
| 11. | 0 | 1 | - |
| 12. | 2 | 1 | 1: FK Violation: Referenced manager_id not found in employees.<br>

<br>2: FK Violation: Referenced branch_id not found in library_branches. |
| 13. | 1 | 1 | FK Violation: Referenced manager_id in library_branches not found in employees. |

---

## Experiment 2

**Model:** `gemini-3.1-pro-preview`
**Parameters:** `temperature = 0.7`, `max_tokens = 65000`

### System Prompt

*(Same as Experiment 1)*

### User Prompt Structure

*(Same as Experiment 1)*

### Results

| No. | Retries | Success | Errors |
| --- | --- | --- | --- |
| 1. | 0 | 1 | - |
| 2. | 1 | 1 | FK Violation: Referenced manager_id in departments not found in employees. |
| 3. | 0 | 1 | - |
| 4. | 1 | 1 | FK Violation: Referenced manager_id in departments not found in employees. |
| 5. | 1 | 1 | FK Violation: Referenced department_id in employees not found in departments. |
| 6. | 0 | 1 | - |
| 7. | 0 | 1 | - |
| 8. | 0 | 1 | - |
| 9. | 0 | 1 | - |
| 10. | 1 | 1 | NotNull Violation: Missing required value for first_name in authors. |
| 11. | 1 | 1 | FK Violation: Referenced manager_id in library_branches not found in employees. |
| 12. | 1 | 1 | NotNull Violation: Missing required value for first_name in authors. |
| 13. | 1 | 1 | FK Violation: Referenced manager_id in library_branches not found in employees. |

---

## Experiment 3

**Model:** `gemini-3.1-pro-preview`
**Parameters:** `temperature = 0.7`, `max_tokens = 65000`

### System Prompt & User Prompt Structure

*(Same as Experiment 1 & 2)*

### Changes

Applied the following Regex to the DDL schema to defer foreign key constraints:

```python
ddl_schema = re.sub(
    r'(?i)(REFERENCES\s+\w+\s*\([^)]+\))(?!\s+DEFERRABLE)', 
    r'\1 DEFERRABLE INITIALLY IMMEDIATE', 
    ddl_schema
)

```

### Results

| No. | Retries | Success | Errors |
| --- | --- | --- | --- |
| 1-12. | 0 | 1 | - |
| 13. | 1 | 1 | NotNull Violation: Missing required value for first_name in authors. |

---

## Experiment 4

**Model:** `gemini-3.1-pro-preview`
**Parameters:** `temperature = 0.7`, `max_tokens = 65000`

### System Prompt Updates

* **Modified Rule 2:** Added *"Never generate a null value for a column that has a NOT NULL constraint, even as a temporary placeholder."*
* **Deleted Rule 6:** Dependency order requirement was removed.

### Changes

* Point 6 was deleted from the prompt.
* *(Implicitly kept the Regex from Exp 3)*

### Results

| No. | Retries | Success | Errors |
| --- | --- | --- | --- |
| 1-13. | 0 | 1 | - |

---

## Experiment 5

**Model:** `gemini-2.0-flash`
**Parameters:** `temperature = 0.7`, `max_tokens = 8000`

### System Prompt Updates

*(Same rule updates as Experiment 4)*

### Changes

* Applied Regex for `DEFERRABLE INITIALLY IMMEDIATE`.
* Point 6 was deleted from the prompt.

### Results

| No. | Retries | Success | Errors |
| --- | --- | --- | --- |
| 1-13. | 0 | 1 | - |

---

## Experiment 6

**Model:** `gemini-2.0-flash`
**Parameters:** `temperature = 0.7`, `max_tokens = 8000`

### System Prompt Updates

Added a new Rule 7:

> 7. All foreign key constraints are DEFERRABLE and checked at the end of the transaction, not per row. This means you can insert data in any order without violating FK constraints. Never set a foreign key column to NULL just to avoid a constraint error - always populate it with a valid reference value.
> 
> 

### Changes

* Applied Regex for `DEFERRABLE INITIALLY IMMEDIATE`.
* Point 6 was deleted from the prompt.
* Added Rule 7.

### Results

| No. | Retries | Success | Errors |
| --- | --- | --- | --- |
| 1-13. | 0 | 1 | - |

---

### **Conclusion**

**In Experiment 5, despite the absence of errors, the model populates the `manager_id` variable with missing values (nulls). Even after adding explicit instructions in Experiment 6, the issue persists. Therefore, let's stick with the `3.1-pro-preview` model, where this problem does not occur.**