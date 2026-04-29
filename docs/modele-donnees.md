---
## ✍️ Contenu de départ

```md
# Modèle de données

Le modèle est construit selon une approche en étoile.

```mermaid
erDiagram
    SALES ||--o{ DATE : date_key
    SALES ||--o{ PRODUCT : product_key
    SALES ||--o{ REGION : region_key
    SALES ||--o{ SALESPERSON : salesperson_key

    SALES {
        decimal Sales
        decimal Profit
        int Orders
    }