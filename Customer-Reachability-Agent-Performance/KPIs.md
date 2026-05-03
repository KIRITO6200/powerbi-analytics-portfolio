
# 📐 KPI Definitions – Reachability & Performance

--------

Stock, = 

CALCULATE(
    COUNTROWS(Intervention),
    InterventionContratClient[code] = "R",
    Intervention[codeReleve] IN { "DEF", "DMS", "TKO", "TOK" }
)

--------

Clients Joint à J = 
CALCULATE(
    COUNTROWS('fichier source'),
    'fichier source'[joint] = 1,
    'fichier source'[D.note] = 'fichier source'[D.cloture]
)

-------

joints = 
CALCULATE(
    DISTINCTCOUNT('fichier source'[numint]),
    'fichier source'[joint] = 1
)

-------

joignabilité = [joints] / [Stock,]

-------

Nbre Tentatives Pour Joindre Un Client = 
DIVIDE(
    SUM('fichier source'[Tentative_CPO_POST]),
    SUM('fichier source'[Joint])
)

------

taux client joint a J = [Clients Joint à J] / [Stock,]

------

taux client joint a la premiere tentative SO = SUM('fichier source'[Joint_1ere_Tentative_CPO]) / [Stock,]

------

Tickets en attente = 
VAR DernierStatutParNumint =
    ADDCOLUMNS (
        SUMMARIZE (
            'fichier source',
            'fichier source'[numint],
            "DerniereDate", MAX('fichier source'[D.note])
        ),
        "DernierStatut",
            CALCULATE (
                SELECTEDVALUE('fichier source'[Statut]),
                FILTER (
                    'fichier source',
                    'fichier source'[numint] = EARLIER('fichier source'[numint])
                    && 'fichier source'[D.note] = [DerniereDate]
                )
            )
    )
RETURN
COUNTROWS (
    FILTER ( DernierStatutParNumint, [DernierStatut] = "En Attente" )
)

------

