<!-- filepath: C:\Users\ukengne\Desktop\Trainings\Github\MonProjet-PowerBI\docs\model-diagram.md -->
# Documentation du Modèle — SalesAnalysis

> 🤖 Fichier généré automatiquement par `scripts/generate_mermaid.py`.
> Ne pas modifier manuellement — toute modification sera écrasée.

## Statistiques

| Élément | Nombre |
| --- | --- |
| Tables | 11 |
| Relations | 9 |
| Colonnes | 48 |
| Mesures DAX | 49 |

## Schéma en étoile (erDiagram)

```mermaid
erDiagram
    Date {
        unknown Date
    }
    KPI_Selector {
        unknown KPI_Selector
        unknown KPI_Selector_Champs
        unknown KPI_Selector_Commande
    }
    Product {
        int ProductKey
        string Product
        decimal Standard_Cost
        string Color
        string Subcategory
        string Category
        string Background_Color_Format
        string Font_Color_Format
    }
    Region {
        int SalesTerritoryKey
        string Region
        string Country
        string Group
    }
    Reseller {
        int ResellerKey
        string Business_Type
        string Reseller
        string City
        string State_Province
        string Country_Region
    }
    Sales {
        string SalesOrderNumber
        date OrderDate
        int ProductKey
        int ResellerKey
        int EmployeeKey
        int SalesTerritoryKey
        int Quantity
        decimal Unit_Price
        string __2_more__
    }
    Salesperson__Performance_ {
        int EmployeeKey
        int EmployeeID
        string Title
        string UPN
        string Salesperson
    }
    Salesperson {
        unknown EmployeeKey
        unknown EmployeeID
        unknown Title
        unknown UPN
        unknown Salesperson
    }
    SalespersonRegion {
        int EmployeeKey
        int SalesTerritoryKey
    }
    Table {
        unknown Column
    }
    Targets {
        int EmployeeID
        decimal TargetAmount
        date TargetMonth
    }
    Product ||--o{ Sales : "ProductKey -> ProductKey"
    Region ||--o{ Sales : "SalesTerritoryKey -> SalesTerritoryKey"
    Reseller ||--o{ Sales : "ResellerKey -> ResellerKey"
    Salesperson__Performance_ ||--o{ SalespersonRegion : "EmployeeKey -> EmployeeKey"
    Region ||--o{ SalespersonRegion : "SalesTerritoryKey -> SalesTerritoryKey"
    Salesperson__Performance_ ||--o{ Targets : "EmployeeID -> EmployeeID"
    Salesperson ||--o{ Sales : "EmployeeKey -> EmployeeKey"
    Date ||--o{ Sales : "Date -> OrderDate"
    Date ||--o{ Targets : "Date -> TargetMonth"
```

## Architecture du modèle (flowchart)

```mermaid
flowchart TD
    subgraph Dims["Dimensions"]
        Date["Date
1 colonnes"]
        Product["Product
8 colonnes"]
        Region["Region
4 colonnes"]
        Reseller["Reseller
6 colonnes"]
        Salesperson__Performance_["Salesperson (Performance)
5 colonnes"]
        Salesperson["Salesperson
5 colonnes"]
        SalespersonRegion["SalespersonRegion
2 colonnes"]
    end
    subgraph Facts["Tables de Faits"]
        KPI_Selector[/"KPI Selector
9 mesures"/]
        Sales[/"Sales
35 mesures"/]
        Table[/"Table
2 mesures"/]
        Targets[/"Targets
3 mesures"/]
    end
    Product -->|ProductKey| Sales
    Region -->|SalesTerritoryKey| Sales
    Reseller -->|ResellerKey| Sales
    Salesperson__Performance_ -->|EmployeeKey| SalespersonRegion
    Region -->|SalesTerritoryKey| SalespersonRegion
    Salesperson__Performance_ -->|EmployeeID| Targets
    Salesperson -->|EmployeeKey| Sales
    Date -->|Date| Sales
    Date -->|Date| Targets
    style KPI_Selector fill:#FAEEDA,stroke:#854F0B
    style Sales fill:#FAEEDA,stroke:#854F0B
    style Table fill:#FAEEDA,stroke:#854F0B
    style Targets fill:#FAEEDA,stroke:#854F0B
    style Date fill:#EBF3FB,stroke:#185FA5
    style Product fill:#EBF3FB,stroke:#185FA5
    style Region fill:#EBF3FB,stroke:#185FA5
    style Reseller fill:#EBF3FB,stroke:#185FA5
    style Salesperson__Performance_ fill:#EBF3FB,stroke:#185FA5
    style Salesperson fill:#EBF3FB,stroke:#185FA5
    style SalespersonRegion fill:#EBF3FB,stroke:#185FA5
    style Facts fill:#FBF5E4,stroke:#C9A84C
    style Dims fill:#E8F0FB,stroke:#1B4F8A
```

## Catalogue des mesures DAX (classDiagram)

```mermaid
classDiagram
    class KPI_Selector {
        +unknown KPI_Selector
        +unknown KPI_Selector_Champs
        +unknown KPI_Selector_Commande
        +measure Selected_KPI_Number()
        +measure Title_Benchmark_By_Category()
        +measure Selected_KPI_Label()
        +measure Selected_KPI_Value()
        +measure Selected_KPI_Measure()
        +measure Title_KPI_By_Month()
        +measure Title_KPI_By_Country()
        +measure Title_KPI_By_Business_Type()
        +measure Title_KPI_By_Sales_Representative()
    }
    class Sales {
        +string SalesOrderNumber
        +date OrderDate
        +int ProductKey
        +int ResellerKey
        +measure Mes_Profit()
        +measure Mes_Profit_Margin()
        +measure Avg_Price()
        +measure Median_Price()
        +measure Min_Price()
        +measure Max_Price()
        +measure Mes_Orders()
        +measure Order_Lines()
        +measure Sales___All_Region()
        +measure Sales___Country()
        +measure Sales___Group()
        +measure Mes_Sales()
        +measure Mes_Cost()
        +measure Mes_LY_Cost()
        +measure Mes_LY_Sales()
        +measure YoY_Sales__()
        +measure YoY_Sales_Direction()
        +measure YoY_Sales_Label()
        +measure Mes_LY_Profit()
        +measure YoY_Profit__()
        +measure YoY_Profit_Label()
        +measure Mes_LY_Orders()
        +measure YoY_Orders__()
        +measure YoY_Orders_Label()
        +measure Mes_LY_Profit_Margin()
        +measure YoY_Profit_Margin__()
        +measure YoY_Profit_Margin_Label()
        +measure Mes_employees()
        +measure Mes_resellers()
        +measure Mes_Products()
        +measure Mes_Salespersons()
        +measure Avg_Deal_Size()
        +measure Profit_Margin_Tooltip()
        +measure Profit_Variance()
        +measure Profit_Variance_Label()
    }
    class Table {
        +unknown Column
        +measure Mes_KPI_Max()
        +measure Mes_KPI_Remaining()
    }
    class Targets {
        +int EmployeeID
        +decimal TargetAmount
        +date TargetMonth
        +measure Target()
        +measure Variance()
        +measure Variance_Margin()
    }
```
