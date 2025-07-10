from aws_cdk import Stack, aws_ec2 as ec2
from constructs import Construct

class NetworkStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # VPC作成
        self.vpc = ec2.Vpc(
            self, "PortfolioVPC",
            max_azs=2,
            nat_gateways=0,
            subnet_configuration=[
                ec2.SubnetConfiguration(name="Public", subnet_type=ec2.SubnetType.PUBLIC, cidr_mask=24),
                ec2.SubnetConfiguration(name="Private", subnet_type=ec2.SubnetType.PRIVATE_ISOLATED, cidr_mask=24)
            ]
        )
        
        # セキュリティグループ作成(ec2,rds,alb)
        self.ec2_sg = ec2.SecurityGroup(
            self, "EC2SecurityGroup",
            vpc=self.vpc,
            description="Security group for EC2 instances",
            allow_all_outbound=True
        )

        self.rds_sg = ec2.SecurityGroup(
            self, "RDSSecurityGroup",
            vpc=self.vpc,
            description="Security group for RDS",
            allow_all_outbound=False
        )
        
        self.alb_sg = ec2.SecurityGroup(
            self, "ALBSecurityGroup",
            vpc=self.vpc,
            description="Security group for ALB",
            allow_all_outbound=False,
        )
        self.ssm_endpoint_sg = ec2.SecurityGroup(
            self, "SSMEPSecurityGroup",
            vpc=self.vpc,
            description="Security group for SSMEP",
            allow_all_outbound=True,
        )
        
        # セキュリテグループのルール設定
        self.ec2_sg.add_ingress_rule(
        peer=self.alb_sg, 
        connection=ec2.Port.tcp(80),
        description="Allow HTTP access from ALB SG"
        )
                
        self.rds_sg.add_ingress_rule(
        peer=self.ec2_sg,
        connection=ec2.Port.tcp(5432),
        description="Allow PostgreSQL access from EC2 SG"
        )
        
        self.alb_sg.add_ingress_rule(
        peer=ec2.Peer.ipv4("0.0.0.0/0"),  
        connection=ec2.Port.tcp(443),
        description="Allow HTTPS from InterNet"
        )
        
        self.alb_sg.add_ingress_rule(
        peer=ec2.Peer.ipv4("0.0.0.0/0"), 
        connection=ec2.Port.tcp(80),
        description="Allow HTTP from InterNet"
        )

        self.ssm_endpoint_sg.add_ingress_rule(
        peer=self.ec2_sg,  
        connection=ec2.Port.tcp(443),
        description="Allow EC2 to access VPC endpoint for SSM"
        )
        
        # SSM用の VPC エンドポイントの追加 
        interface_endpoints = [
            "com.amazonaws." + Stack.of(self).region + ".ssm",
            "com.amazonaws." + Stack.of(self).region + ".ec2messages",
            "com.amazonaws." + Stack.of(self).region + ".ssmmessages"
        ]

        for service in interface_endpoints:
            ec2.InterfaceVpcEndpoint(
                self, f"{service.split('.')[-1]}Endpoint",
                vpc=self.vpc,
                service=ec2.InterfaceVpcEndpointService(
                    name=service,
                    port=443
                ),
                private_dns_enabled=True,
                subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
                security_groups=[self.ssm_endpoint_sg]  # 必要に応じてSG変更
            )