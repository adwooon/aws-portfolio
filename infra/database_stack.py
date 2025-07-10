from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct

class DatabaseStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, rds_sg: ec2.SecurityGroup, **kwargs):
        super().__init__(scope, id, **kwargs)

        # RDSインスタンス（PostgreSQL）
        self.db_instance = rds.DatabaseInstance(
            self, "AppRDS",
            engine=rds.DatabaseInstanceEngine.postgres(  
                version=rds.PostgresEngineVersion.VER_15
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO
            ),
            vpc=vpc,
            multi_az=False,
            allocated_storage=20,
            max_allocated_storage=20,
            security_groups=[rds_sg],
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            publicly_accessible=False,
            database_name="appdb",
            credentials=rds.Credentials.from_generated_secret("db_admin"),
            removal_policy=RemovalPolicy.RETAIN
        )
        
        # RDSエンドポイント表示
        CfnOutput(self, "AppRDS_Endpoint", value=self.db_instance.db_instance_endpoint_address)