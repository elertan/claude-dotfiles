# Normal Forms Reference

## Quick Reference Table

| NF | Requirement | Eliminates |
|----|-------------|------------|
| **1NF** | Atomic values, unique rows | Repeating groups |
| **2NF** | 1NF + no partial dependencies | Partial dependencies |
| **3NF** | 2NF + no transitive dependencies | Transitive dependencies |
| **BCNF** | Every determinant is a superkey | All FD anomalies |

## Functional Dependencies (FDs)

A functional dependency X → Y means: for any two rows with the same X value, the Y values must be equal.

```
Example: employee_id → employee_name
If employee_id = 101, then employee_name is always "Alice"
```

**Key terms:**
- **Determinant**: Left side of FD (X in X → Y)
- **Dependent**: Right side of FD (Y in X → Y)
- **Candidate key**: Minimal set of attributes that determines all others
- **Superkey**: Any set containing a candidate key
- **Prime attribute**: Part of some candidate key
- **Non-prime attribute**: Not part of any candidate key

## First Normal Form (1NF)

**Requirements:**
1. All values are atomic (no lists, arrays, nested structures)
2. Each row is unique (has a key)
3. No repeating groups

**Violation example:**
```
| order_id | customer | products              |
|----------|----------|-----------------------|
| 1        | Alice    | apple, banana, cherry |
```

**Fixed (1NF):**
```
| order_id | customer | product |
|----------|----------|---------|
| 1        | Alice    | apple   |
| 1        | Alice    | banana  |
| 1        | Alice    | cherry  |
```

## Second Normal Form (2NF)

**Requirements:**
1. Is in 1NF
2. No partial dependencies (non-prime attributes depend on full candidate key)

Only relevant when candidate key is composite (multiple columns).

**Violation example:**
```
Key: {student_id, course_id}

| student_id | course_id | student_name | course_name | grade |
|------------|-----------|--------------|-------------|-------|

FDs:
- {student_id, course_id} → grade (full dependency - OK)
- student_id → student_name (PARTIAL - violates 2NF)
- course_id → course_name (PARTIAL - violates 2NF)
```

**Fixed (2NF):**
```
Students: student_id → student_name
Courses: course_id → course_name
Enrollments: {student_id, course_id} → grade
```

## Third Normal Form (3NF)

**Requirements:**
1. Is in 2NF
2. No transitive dependencies (non-prime → non-prime)

**Violation example:**
```
Key: employee_id

| employee_id | employee_name | dept_id | dept_name |

FDs:
- employee_id → dept_id (OK)
- dept_id → dept_name (TRANSITIVE - violates 3NF)
```

**Fixed (3NF):**
```
Employees: employee_id → {employee_name, dept_id}
Departments: dept_id → dept_name
```

## Boyce-Codd Normal Form (BCNF)

**Requirements:**
1. Is in 3NF
2. For every FD X → Y, X is a superkey

Stricter than 3NF. Handles edge cases where prime attributes have dependencies.

**Violation example:**
```
Key: {student, subject}

| student | subject | teacher |

FDs:
- {student, subject} → teacher
- teacher → subject (teacher determines subject - violates BCNF)
```

**Fixed (BCNF):**
```
TeacherSubjects: teacher → subject
StudentTeachers: {student, teacher} (key)
```

## Decision Tree: Identifying Current Normal Form

```
1. Are all values atomic and rows unique?
   NO → UNF (Unnormalized)
   YES → Continue

2. Are there partial dependencies on composite key?
   YES → 1NF
   NO → Continue

3. Are there transitive dependencies (non-prime → non-prime)?
   YES → 2NF
   NO → Continue

4. Are all determinants superkeys?
   NO → 3NF
   YES → BCNF
```

## Common Patterns to Watch For

### Pattern 1: Lookup Values
```
| order_id | product_id | product_name | product_category |
```
`product_id → {product_name, product_category}` indicates need for Products table.

### Pattern 2: Repeated Groups
```
| customer_id | phone1 | phone2 | phone3 |
```
Violates 1NF. Create CustomerPhones junction table.

### Pattern 3: Derived/Calculated Values
```
| order_id | quantity | unit_price | total |
```
If `total = quantity * unit_price`, consider removing `total` (derived).

### Pattern 4: Address Components
```
| customer_id | city | state | zip |
```
If `zip → {city, state}`, extract to Locations table.
