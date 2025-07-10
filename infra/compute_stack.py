from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_autoscaling as autoscaling,
    aws_elasticloadbalancingv2 as elbv2,
    aws_cloudwatch as cloudwatch,
    Duration
)
from constructs import Construct

class ComputeStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, ec2_sg: ec2.SecurityGroup, alb_sg: ec2.SecurityGroup, **kwargs):
        super().__init__(scope, id, **kwargs)

        # EC2にhttpdをインストールしindex.htmlを配置
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            "yum update -y",
            "yum install -y httpd",
            "systemctl start httpd",
            "systemctl enable httpd",
            "echo '<h1>OK from Auto Scaling Group</h1>' > /var/www/html/index.html"
        )
        
        # EC2用のAutoScaling Group
        self.asg = autoscaling.AutoScalingGroup(
            self, "AppAsg",
            vpc=vpc,
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2023(),
            security_group=ec2_sg,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
            desired_capacity=2,
            min_capacity=1,
            max_capacity=3,
            user_data=user_data
        )
        
        # CloudWatch メトリクスを定義(cpu使用率)
        cpu_metric = cloudwatch.Metric(
        namespace="AWS/EC2",
        metric_name="CPUUtilization",
        dimensions_map={
            "AutoScalingGroupName": self.asg.auto_scaling_group_name
        },
        period=Duration.minutes(1)
        )

        # スケーリングポリシー: CPU使用率によるスケーリング
        self.asg.scale_on_metric("CpuScalingPolicy",
            metric=cpu_metric,
            scaling_steps=[
                autoscaling.ScalingInterval(upper=30, change=-1),  # CPU < 70% → スケールイン
                autoscaling.ScalingInterval(lower=70, change=+1),  # CPU > 70% → スケールアウト
            ],
            adjustment_type=autoscaling.AdjustmentType.CHANGE_IN_CAPACITY,
            estimated_instance_warmup=Duration.seconds(120)
        )
        
        # ALB（Application Load Balancer）
        self.alb = elbv2.ApplicationLoadBalancer(
            self, "AppALB",
            vpc=vpc,
            internet_facing=True,
            load_balancer_name="AppALB",
            security_group=alb_sg,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
        )

        # ALBのリスナー設定（HTTP）
        listener = self.alb.add_listener("HttpListener", port=80)
        target_group = listener.add_targets("AppFleet", port=80, targets=[self.asg])

        # Health check（オプション：より詳細に調整可能）
        target_group.configure_health_check(path="/", healthy_http_codes="200")
