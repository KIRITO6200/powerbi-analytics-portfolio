
# 📐 KPI Definitions – Call Center Dashboard

 TREATED CALLS = 
COALESCE(
    CALCULATE(
        DISTINCTCOUNT('log_detailed_1754571598'[CallId]),
        'log_detailed_1754571598'[QualifName] = "Traité",
        'log_detailed_1754571598'[Type] = "E",
        'log_detailed_1754571598'[Statut] = "Communication"
    ),
    0
)

---------------

calls recieved = DISTINCTCOUNT('log_detailed_1754571598'[CallId])
---------------
Abandoned calls = 
COALESCE(
    CALCULATE(
        DISTINCTCOUNT('log_detailed_1754571598'[CallId]),
        'log_detailed_1754571598'[QualifName] = "Abandon"
    ),
    0
)

QS = 
COALESCE(
    DIVIDE(
        [treated calls],
        DISTINCTCOUNT('log_detailed_1754571598'[CallId])
    ),
    0
)

-----------------------

total time of calls  = 
CALCULATE(
    SUM('log_detailed_1754571598'[Duree]),
    'log_detailed_1754571598'[QualifName] = "Traité",
    'log_detailed_1754571598'[Statut] = "Communication",
    'log_detailed_1754571598'[Agent] <> ""
)
+
CALCULATE(
    SUM('log_detailed_1754571598'[Duree]),
    'log_detailed_1754571598'[QualifName] = "Traité",
    'log_detailed_1754571598'[Statut] = "Mise en Attente",
    'log_detailed_1754571598'[Agent] <> ""
)
        +
        CALCULATE(
            SUM('log_detailed_1754571598'[Duree]),
            'log_detailed_1754571598'[QualifName] = "Traité",
            'log_detailed_1754571598'[Statut] = "Cloture d'appel",
            'log_detailed_1754571598'[Agent] <> ""
        )



------- kpis related to agents

Top 3 Agents (abandoné, Type E) = 
VAR AgentsVisible =
    ALLSELECTED('log_detailed_1754571598'[Agent])  -- compare les agents visibles tout en gardant les autres slicers (date, équipe, file…)
VAR AgentsAvecValeur =
    ADDCOLUMNS(
        AgentsVisible,
        "NbAbondone", [Abandonned calls]
    )
VAR Top3 =
    TOPN(
        3,
        AgentsAvecValeur,
        [NbAbondone], DESC,
        'log_detailed_1754571598'[Agent], ASC
    )
RETURN
    CONCATENATEX(
        Top3,
        'log_detailed_1754571598'[Agent] & " (" & FORMAT([NbAbondone], "#,0") & ")",
        ", "
    )
    
------------------------

Top 3 Agents (Traités, Type E) = 
VAR AgentsVisible =
    ALLSELECTED('log_detailed_1754571598'[Agent])  -- compare les agents visibles tout en gardant les autres slicers (date, équipe, file…)
VAR AgentsAvecValeur =
    ADDCOLUMNS(
        AgentsVisible,
        "NbTraitesE", [treated calls]
    )
VAR Top3 =
    TOPN(
        3,
        AgentsAvecValeur,
        [NbTraitesE], DESC,
        'log_detailed_1754571598'[Agent], ASC
    )
RETURN
    CONCATENATEX(
        Top3,
        'log_detailed_1754571598'[Agent] & " (" & FORMAT([NbTraitesE], "#,0") & ")",
        ", "
    )


