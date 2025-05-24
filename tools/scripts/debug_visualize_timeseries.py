import matplotlib.pyplot as plt
import pandas as pd

from ekaine.postgresql import SessionLocal

session = SessionLocal()
with session.connection() as conn:
    df = pd.read_sql(
        """
    SELECT timestamp, s.name as system_name, f.name as faction_name, influence
    FROM timescaledb.faction_presences fp
    INNER JOIN core.systems s
    ON fp.system_id = s.id
    INNER JOIN core.factions f
    ON fp.faction_id = f.id
    WHERE timestamp > now() - interval '1 day'
    and s.id = 48694
    """,
        conn,
    )

    grouped = df.groupby(["system_name", "faction_name"])
    plt.figure(figsize=(12, 6))

    # Plot each group as its own line
    for (system_name, faction_name), group in grouped:
        label = f"{system_name} - {faction_name}"
        print(label)
        plt.plot(group["timestamp"], group["influence"], label=label)

    plt.xlabel("Time")
    plt.ylabel("Influence")
    plt.title("Faction Influence Over Time")
    plt.legend(fontsize="small", loc="upper right")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
