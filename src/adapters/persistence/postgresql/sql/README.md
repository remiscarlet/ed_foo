## Organization

### Functions
- If the function is in the `derived` schema, write in `sql`
    - This ensures that the inline use of anything from the `derived` schema (including views) can be efficiently optimized by the Postgres query planner.
- If the function is in the `api` schema, write in `PL/pgSQL`
    - Anything from the `api` layer is understood to be an entrypoint and thus will not be used inline, therefore we don't care about nested query planners.
