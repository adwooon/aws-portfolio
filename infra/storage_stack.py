from aws_cdk import (
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_s3_deployment as s3deploy,
    CfnOutput,
    RemovalPolicy,
    Stack,
)
from constructs import Construct
import os

class StorageStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # S3バケット作成（非公開）
        self.site_bucket = s3.Bucket(
            self, "StaticSiteBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
        
        # OAI（CloudFrontのS3アクセス専用ID）を作成
        oai = cloudfront.OriginAccessIdentity(self, "OAI")

        # CloudFrontディストリビューション作成
        self.distribution = cloudfront.Distribution(
            self, "SiteDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(self.site_bucket, origin_access_identity=oai),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
            ),
            default_root_object="index.html"
        )

        # S3ポリシーをOAI用に追加
        self.site_bucket.grant_read(oai)

        # 静的ファイルをS3にアップロード
        s3deploy.BucketDeployment(
            self, "DeployStaticContent",
            sources=[s3deploy.Source.asset(os.path.join(os.getcwd(), "static"))],
            destination_bucket=self.site_bucket,
            distribution=self.distribution,
            distribution_paths=["/*"]
        )

        # 出力
        self.cloudfront_url = self.distribution.distribution_domain_name
        
        # CloudFrontドメインをターミナルに表示
        CfnOutput(
            self, "CloudFrontURL",
            value=self.distribution.distribution_domain_name,
            description="The URL of the CloudFront distribution",
        )