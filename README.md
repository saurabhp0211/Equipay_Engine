EquiPay - Distributed Expense Settlement Engine

Overview

EquiPay is a highly concurrent backend service for an expense-sharing application, built using FastAPI, PostgreSQL, and Redis.

Originally built as a foundational expense-splitting assignment, this project has been architected into a production-ready microservice. It features a flexible mathematical engine for complex split types, strict ACID-compliant database transactions, API rate limiting, JWT-based authentication, and a Greedy Debt Simplification algorithm to minimize total P2P transactions.

🚀 Setup & Installation (Dockerized)

The entire infrastructure (FastAPI, PostgreSQL, Redis) is containerized for seamless, one-click deployments.

1. Clone the repository:

git clone https://github.com/saurabhp0211/Equipay_Engine.git
cd decentro_expense_service


2. Configure Environment Variables:
Ensure your .env file is populated with your database credentials, JWT Secret, and Razorpay API keys.

3. Boot the Microservices:

docker compose up --build


4. Run Database Migrations:
In a separate terminal, apply the Alembic schema migrations to your PostgreSQL instance:

docker compose exec api alembic upgrade head


5. View the API Docs:
Navigate to http://localhost:8000/docs to use the interactive Swagger UI. You must create a user and authenticate via the /login endpoint to receive a Bearer token for protected routes.

🗄️ Database Design (PostgreSQL)

I designed a highly normalized relational schema to clearly separate the "Master Receipt" (who swiped their card) from the "Ledger" (who owes what).

users: Core user details with hashed passwords.

groups: Group metadata.

group_members: An association table handling the Many-to-Many relationship.

expenses: The master receipt (e.g., Mohit pays ₹3000 for a hotel).

expense_splits: The individual ledger. This table holds the exact, calculated debt for every person involved, with a Foreign Key back to the master expenses table.

Data Integrity & Concurrency: I utilized SQLAlchemy's ondelete="CASCADE" to prevent orphan data. Critical financial transactions are wrapped in strict try...except blocks with db.rollback() to guarantee ACID compliance and prevent half-saved ledger states.

💡 Architectural Features & Design Decisions

1. Two-Pointer Greedy Debt Simplification

Instead of returning a raw list of who owes whom (which creates a messy web of micro-debts), the /groups/{group_id}/balances endpoint runs a Two-Pointer Greedy Algorithm. It calculates the net balances of all users and simplifies the debt matrix in $O(N \log N)$ time, ensuring the minimum possible number of transactions are required to settle the group.

2. Redis Caching & Cache Invalidation

Because the debt simplification algorithm is computationally heavy, the calculated balances are cached in Redis. This reduces the $O(N \log N)$ calculation down to an $O(1)$ memory lookup. I implemented strict cache invalidation hooks: the exact moment a new expense is successfully committed to Postgres, the specific group's cache is purged.

3. Razorpay Integration & State Management

I integrated the Razorpay API to allow users to actually settle their debts. The /settlements/razorpay-order endpoint enforces strict validation to ensure users cannot overpay or settle debts they do not owe, before generating a secure order payload for the frontend.

4. Asynchronous Background Tasks

To ensure the main event loop isn't blocked by high-latency I/O operations (like sending email receipts or payment notifications), I implemented FastAPI BackgroundTasks. The API immediately returns a 201 Created response to the user while the notification executes asynchronously in the background.

5. Security Guardrails (Auth & Rate Limiting)

JWT OAuth2: All financial and group endpoints are secured via Dependency Injection (get_current_user), blocking cross-tenant data leaks and IDOR vulnerabilities.

SlowAPI Rate Limiting: Endpoints are protected against brute-force and DoS attacks (e.g., the /login route is strictly limited to 5 requests/minute per IP).

6. The Math Engine (EXACT & PERCENT Splits)

I built EXACT and PERCENT splits to mimic real-world scenarios. I handled validation dynamically using Pydantic and custom FastAPI exceptions. If a user submits a percentage split that doesn't exactly equal 100%, the API intercepts it and throws a 400 Bad Request before it ever touches the database.

🔮 Improvements with More Time

Given more time, I plan to implement the following enterprise-grade features:

Idempotency Keys: Implement an X-Idempotency-Key header cached in Redis to prevent Time-Of-Check to Time-Of-Use (TOCTOU) race conditions, guaranteeing users are never double-charged if they double-click the "Pay" button.

Cloud Integration (AWS): Utilize boto3 to export monthly group spending analytics to an Amazon S3 bucket, returning presigned URLs to the user for PDF/CSV downloads.

Automated CI/CD: Implement a GitHub Actions pipeline to automatically run Pytest suites and trigger rolling deployments to AWS ECS upon pushes to the main branch.
