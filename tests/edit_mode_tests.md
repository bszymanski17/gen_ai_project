| Prompt (Instruction) | Success | Test Type / Formal Description |
| :--- | :---: | :--- |
| Add an employee who works in department_id=12 | 1 | **INS-DATA:** Inserting a new record linked to an existing Foreign Key (FK). |
| Increase restaurant_id by 1 in the menu table | 1 | **MOD-FK:** Modifying a Foreign Key value in a child table (updating a relationship). |
| Delate all restaurant from New York | 1 | **DEL-DATA:** Conditional deletion of records (testing cascading deletes in relationships). |
| Increase restaurant_id by 1 in the restaurants table | 1 | **MOD-PK:** Modifying a Primary Key (PK) in a parent table (requires updating associated FKs). |
| For order_id = 3 replace the restaurant_id  with 300 | 1 | **MOD-FK:** Targeted Foreign Key update (assigning a new reference) for a specific order. |
| Change the author ID to 7 for the book with ID 4. | 1 | **MOD-FK:** Updating a relationship link between entities (Book → Author). |
