# Revenue Growth %

```DAX
Revenue Growth % =
DIVIDE(
    TOTALYTD(SUM('Fact Billing'[Total Amount]), 'Dim Date'[Full Date])
    -
    CALCULATE(
        TOTALYTD(SUM('Fact Billing'[Total Amount]),'Dim Date'[Full Date]),
        SAMEPERIODLASTYEAR('Dim Date'[Full Date])
    ),
    CALCULATE(
        TOTALYTD(SUM('Fact Billing'[Total Amount]), 'Dim Date'[Full Date]),
        SAMEPERIODLASTYEAR('Dim Date'[Full Date])
    ),
    0
)
```

# Avg Revenue Per Patient

```DAX
Avg Revenue Per Patient =
DIVIDE(
    SUM('Fact Billing'[Total Amount]),
    DISTINCTCOUNT('Fact Billing'[Patient Key])
)
```