"""An AWS Python Pulumi program"""

import pulumi
from pulumi_aws import s3, ec2

# Create an AWS resource (S3 Bucket)
bucket = s3.Bucket("my-bucket")

# Export the name of the bucket
pulumi.export("bucket_name", bucket.id)

# PUBLIC KEY
aws_public_key = ec2.KeyPair(
    "aws_public_key",
    public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCjOcXLi6/PjesaPn5js08+OYfHzQuQ6BzjrLd2hVo6jc93WrYlaEMzfMp969JQ29L8+KbBjwQvwm/jZ/31Usg12ceEySGOZXY9ycQKWc53xWDYrm6Gkr/ScVhfXNLDjssN7xG1kqa1TaVNnAenAY9npBJyh3WCgXQ6xQR9809NpjbOtr5pPdAQE7CU4JFOwnL+0Es5gudb3I8bHULt+pOUfP4d5Cav9/Egfd5XfoSfCRQJC8sJPLLrHLLRxJp/xHIVQdNpjWu/ttYOE3TpaHTQfJjPJPBci3TfX9JQiS0UnpoB3BeKXo/xrHKQ0t4OJOBt20NNFAIbDYMnszSLaj+bXcHHejyRg6w6KVKKnY5Iua6xEFQXXjWMDM5Vt+p0FzDRPelzB/9AzUm2U9LkPXz+y7O5vIn41GHJFMiijqDLDcmhrME89cFAmdFQmObsCwMSiRYmPyOQXNQ4YAGi+UxDT/aclKfJB+T39P4vULcd7nWlaPqGAOHWmreLsjQq127Me1NOWxv31sE3SYDDtszQP8fjAfs5UYxOFfXpZX5VHqwEXZafyIhJfHj0J9BWuuZIQJySsB6xsGizZDE0fvKhAmlcqWtYSe3ipxMPXQeXlFgMeqFS1jMtyq/ckawxuGNFx9XgyN46dLixIMJi8bKdthD39pGWnsUpdP4VB6H57Q== nabil@zenbook",
)


# SECURITY GROUPS
sg = ec2.SecurityGroup(
    "webserver-security-group", description="security group for webservers"
)

allow_ssh = ec2.SecurityGroupRule(
    "AllowSSH",
    type="ingress",
    from_port=22,
    to_port=22,
    protocol="tcp",
    cidr_blocks=["0.0.0.0/0"],
    security_group_id=sg.id,
)

allow_http = ec2.SecurityGroupRule(
    "AllowHTTP",
    type="ingress",
    from_port=80,
    to_port=80,
    protocol="tcp",
    cidr_blocks=["0.0.0.0/0"],
    security_group_id=sg.id,
)

allow_all = ec2.SecurityGroupRule(
    "AllowAll",
    type="ingress",
    from_port=0,
    to_port=0,
    protocol="-1",
    cidr_blocks=["0.0.0.0/0"],
    security_group_id=sg.id,
)

# EC2 INSTANCES
ec2_instance = ec2.Instance(
    "super-awesome-ec2-instance",
    ami="ami-06dd92ecc74fdfb36",
    instance_type="t2.micro",
    associate_public_ip_address=True,
    key_name=aws_public_key.key_name,
    tags={"Name": "webserver"},
    vpc_security_group_ids=[sg.id],
)

pulumi.export("public_ip", ec2_instance.public_ip)
pulumi.export("instance_url", ec2_instance.public_dns)
