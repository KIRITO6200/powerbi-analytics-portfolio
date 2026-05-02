
# 📐 KPI Definitions – Sogetrel belgium Interventions

interventions = CALCULATE(COUNTROWS(sheet1))

---------

Interventions Annulées = COALESCE(
CALCULATE([interventions],
    KEEPFILTERS(Sheet1[StatutIntervention] = "Annulation")
),0)

-----------

interventions realisé dans le créneaux = COALESCE(
CALCULATE(
    COUNTROWS(
        FILTER(
            Sheet1,
            Sheet1[Dépassement (min)] = 0
        )
    )
),0)

--------

interventions realisé hors créneaux = 
CALCULATE(
    COUNTROWS(
        FILTER(
            Sheet1,
            Sheet1[Dépassement (min)] <> 0
        )
    )
)

--------

Interventions Réalisées = 
CALCULATE([interventions],
    KEEPFILTERS(Sheet1[StatutIntervention] = "Confirmation")
)

---------

moyen de durée passé dans l'intervention = SUM(Sheet1[TempsPasseMinutes]) / [interventions]

---------

nombre des clients absents = COALESCE(
    CALCULATE(
        COUNTROWS(
            FILTER(Sheet1, Sheet1[RaisonAnnulation] = "Le client n'est pas à la maison")
        )
    ),0)

--------

Nombre des depassement = COALESCE(
CALCULATE(
    COUNTROWS(
        FILTER(
            Sheet1,
            Sheet1[Dépassement (min)] <> 0
        )
    )
),0)

--------

Nombre des fois arrivée dans le créneau = 
CALCULATE(
    COUNTROWS(
        FILTER(
            Sheet1,
            Sheet1[Arrivée dans créneau (flag)] = 1
        )
    )
)

--------

Nombre des fois arrivée hors créneau = COALESCE(
CALCULATE(
    COUNTROWS(
        FILTER(
            Sheet1,
            Sheet1[Arrivée dans créneau (flag)] = 0
        )
    )
),0)

--------

nombre des fois des tests internet = 
    CALCULATE(
        COUNTROWS(
            FILTER(Sheet1, Sheet1[Test_OK_Flag] = TRUE())
        )
    )

--------

Taux arrivée dans créneau (tolérance) = 
VAR tol = [Tolérance (min)]
RETURN
DIVIDE(
    SUMX(
        Sheet1,
        VAR s = Sheet1[DateIntervention] + Sheet1[TimeSlotStart]
        VAR e = Sheet1[DateIntervention] + Sheet1[TimeSlotEnd] + (tol/1440.0)
        VAR a = IF(
            NOT ISBLANK(Sheet1[HeureArrivee]),
            Sheet1[DateIntervention] + Sheet1[HeureArrivee]
        )
        RETURN IF(NOT ISBLANK(a) && a >= s && a <= e, 1, 0)
    ),
    [Interventions Réalisées]
)


--------

Taux d'absence client = 
VAR TotalClients = COUNTROWS(Sheet1)
VAR ClientsAbsents =
    CALCULATE(
        COUNTROWS(
            FILTER(Sheet1, Sheet1[ClientAbsent_Flag] = TRUE())
        )
    )
RETURN
IF(TotalClients = 0, 0, DIVIDE(ClientsAbsents, TotalClients, 0))

--------

Taux d'annulation = DIVIDE([Interventions Annulées], [Interventions])

--------

taux d'interventions réalisées au créneaux = COALESCE(( [interventions realisé dans le créneaux] / [interventions]),0)

--------

taux de depassement = COALESCE(([Nombre des depassement] / [interventions]),0)

--------

taux realisation = COALESCE(([Interventions Réalisées] / [interventions]),0)

-------

fin
