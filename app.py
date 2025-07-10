#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infra.network_stack import NetworkStack
from infra.storage_stack import StorageStack
from infra.compute_stack import ComputeStack
from infra.database_stack import DatabaseStack


app = cdk.App()

# VPCとセキュリティグループなどの基盤ネットワーク
network_stack = NetworkStack(app, "NetworkStack")

# ストレージ（S3 & CloudFront）
storage_stack = StorageStack(app, "StorageStack")

# EC2 + ALB
compute_stack = ComputeStack(
    app,
    "ComputeStack",
    vpc=network_stack.vpc,
    ec2_sg=network_stack.ec2_sg,
    alb_sg=network_stack.alb_sg
)

# RDS
database_stack = DatabaseStack(
    app,
    "DatabaseStack",
    vpc=network_stack.vpc,
    rds_sg=network_stack.rds_sg
)
app.synth()
