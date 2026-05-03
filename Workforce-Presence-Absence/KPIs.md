Présence = 
COALESCE (
    CALCULATE (
        SUM ( 'réalisé'[dure Heures] ),
        'réalisé'[Libellé] IN {
            "AE",
            "Facturation",
            "MER",
            "Planification",
            "ESC/RECLA",
            "CLÔTURE",
            "POST",
            "PRO PME",
            "BO",
            "Management_Orange",
            "GEM & TAC",
            "Tâche non affectée",
            "PRE-Intervention",
            "Formation Initiale"
        }
    ),
    0
)

-------

Absence = 
COALESCE (
    CALCULATE (
        SUM ( 'réalisé'[dure Heures] ),
        KEEPFILTERS (
            'réalisé'[Libellé] IN {
                "Absence justifiée",
                "Absence Longue Durée",
                "Absence injustifiée"
            }
        )
    ),
    0
)

----

Décharge = COALESCE(
CALCULATE (
    SUM ( 'réalisé'[dure Heures] ),
    KEEPFILTERS ( 'réalisé'[Libellé] IN { "Débits", "Décharges" } )
),0)


-----

duré de travaile planifié = COALESCE(( SUM('Planing (2)'[dure Heures])),0)

----

Jours Absence = 
VAR Heures = [Absence]   
RETURN
IF ( Heures >= 8.75, 1.00, 0.00 )


----

nb retard = COALESCE(CALCULATE(COUNTROWS('réalisé'),'réalisé'[Libellé] = "RETARD"),0)

----

Retard = COALESCE(
CALCULATE (
    SUM ( 'réalisé'[dure Heures] ),
    KEEPFILTERS ( 'réalisé'[Libellé] = "RETARD" )
),0)


----

