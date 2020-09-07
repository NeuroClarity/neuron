from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_ec2 as ec2,
    aws_efs as efs,
)


class AnalyticsLambdaStack(core.Stack):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc.from_lookup(self, "defaultVPC", vpc_id="vpc-09ec9171")

        # Defines an AWS Lambda resource
        my_lambda = _lambda.Function(
            self, 'AnalyticsJobFunction',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.asset('lambda'),
            handler='main.analytics_job_handler',
            vpc=vpc,
            allow_public_subnet=True,
            #vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE),
            timeout=core.Duration.seconds(900), # set timeout to max for lambda -- 15 minutes
            memory_size=3008,
        )
