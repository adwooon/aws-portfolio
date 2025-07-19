# AWS Infrastructure Portfolio (CDK × Python)
AWS CDK（Python）を使って構築したインフラ構成のポートフォリオです。  
VPC / EC2 / RDS / ALB / S3 / CloudFront などをIaCでコード化しています。

##  使用技術・サービス一覧

- **AWS CDK (Python)**
- **VPC**（Public / PrivateSubnet, 2AZ）
- **EC2（Auto Scaling Group + Apache）**
- **ALB（Application Load Balancer）**
- **RDS（PostgreSQL）**
- **S3 + CloudFront（静的コンテンツ配信）**
- **SSM + VPCエンドポイント**
- **セキュリティグループの適切な制御**

## デプロイ手順

PowerShell上で以下を順に実行します：

# 仮想環境作成・起動
python -m venv .venv
.venv\Scripts\Activate.ps1

# 依存ライブラリインストール
pip install -r requirements.txt

# CDK初期化（初回のみ）
cdk bootstrap

# CDKデプロイ（全スタック）
cdk deploy --all

意識した点
UserData を用いて EC2起動時に Apache を自動インストール

CloudFront + S3 を使った静的ファイル高速配信

EC2 → RDS、ALB → EC2、SSM → EC2 など最小限の通信のみ許可

RDS は RemovalPolicy.RETAIN を指定して、誤削除を防止

スケーリングポリシー実装：CPU 70% でスケールアウト、30% でスケールイン。

静的コンテンツ自動デプロイ：staticディレクトリの中身をCloudFront経由で即時配信。

パブリックアクセス制御：S3バケットは完全非公開 + OAI経由でのみアクセス許可。

# Welcome to your CDK Python project!

This is a blank project for CDK development with Python.

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!