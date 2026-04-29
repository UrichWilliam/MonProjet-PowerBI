# Architecture du rapport

## Vue d’ensemble

```mermaid
flowchart TB
    Sources[Sources de données]
    Model[Modèle sémantique]
    Measures[Mesures DAX]
    Params[KPI Selector]
    Report[Rapport Power BI]

    Sources --> Model
    Model --> Measures
    Measures --> Params
    Params --> Report
