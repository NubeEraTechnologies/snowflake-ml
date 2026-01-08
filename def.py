import snowflake.snowpark as snowpark
from snowflake.snowpark.types import StringType, IntegerType


def main(session: snowpark.Session):

    # ✅ Define UDF logic INSIDE main
    def customer_risk_py(age, spend):
        if age is None or spend is None:
            return "UNKNOWN"

        if age > 45 and spend > 70000:
            return "HIGH_RISK"
        elif spend > 40000:
            return "MEDIUM_RISK"
        else:
            return "LOW_RISK"

    # ✅ Register UDF
    session.udf.register(
        func=customer_risk_py,
        name="customer_risk",
        input_types=[IntegerType(), IntegerType()],
        return_type=StringType(),
        is_permanent=True,
        stage_location="@~",
        replace=True
    )
    

    return "✅ customer_risk UDF registered successfully"
