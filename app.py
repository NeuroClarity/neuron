from aws_cdk import core

from deploy.cdk_lambda import AnalyticsLambdaStack


app = core.App()
AnalyticsLambdaStack(app, "neuron", env={
        'account': '471943556279',
        'region': 'us-west-2'
        }
    )

app.synth()
