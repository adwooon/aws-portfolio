import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_portfolio_infra.aws_portfolio_infra_stack import AwsPortfolioInfraStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_portfolio_infra/aws_portfolio_infra_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsPortfolioInfraStack(app, "aws-portfolio-infra")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
